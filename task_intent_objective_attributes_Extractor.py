import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import verbnet
from textblob import TextBlob
from nltk.corpus import wordnet

stopWords = nltk.corpus.stopwords.words('english')
stopWords.append('go')

class task:
    def __init__(self,text,**kwargs):
        self.text = text
        self.raw = text
        self.intent = False
        self.attributes = False
        self.action_upon = False
        self.discardedVerbs = []
        self.discardedNouns = []
        if bool(kwargs) is True:
            if kwargs['preprocessing']:
                self.preprocessing()

    def get_tokens(self):
        '''retruns the sentence as tokens'''
        return nltk.word_tokenize(self.text)

    def get_POS(self):
        '''return the POS of the tokens'''
        #return nltk.pos_tag(self.get_tokens())
        return TextBlob(self.raw).tags

    def preprocessing(self):
        '''
            Preprocessing on the text
            1 : remove the any unwanted character
            2 : lemmatize the word
        '''
        self.text = re.sub('[^A-Za-z0-9 -/\']','',self.text)    #removes everything except alnum, space, single quotes
        L = self.get_tokens()
        lemma = WordNetLemmatizer()
        L = [lemma.lemmatize(i) for i in L]
        self.text = ' '.join(L)

    def filterOutVerbs(self,L):
        L = list(set(L))
        lemma = WordNetLemmatizer()
        #taking the verb lemas of the words in L
        L = [lemma.lemmatize(i, pos='v') for i in L]
        print('L',L)
        print(verbnet.lemmas())
        #extracting the verbs from the L which are in Wordnet's Verb and are a stopWord
        L = [i for i in L if i in verbnet.lemmas() and i not in stopWords]
        L = list(set(L))
        return L

    def get_POS_tree(self,chunk):
        return nltk.RegexpParser(chunk).parse(self.get_POS())

    def find_pos(self,w):
        tokens = self.get_tokens()
        for i in range(len(tokens)):
            if tokens[i]==w:
                return i
        else:
            return -1

    def get_intent(self):
        L = []

        chunkGramForNounVerb = r'''NV: {<VB.?><.*>*<NN.?>+}
                            }<VBP|VBZ|PRP.?|RB|W.*|JJ.?|CD|TO|IN|DT>+{'''

        chunkGramForOnlyVerb = r'''VR: {<VB.?>}
                            }<VBP|VBZ>+{'''

        tree = self.get_POS_tree(chunkGramForNounVerb)
        obj = []
        series = []

        for subtree in tree.subtrees(filter=lambda t: t.label() == 'NV'):
            if len(subtree.leaves())>1:
                series = subtree.leaves()
            obj = obj + [s for s in subtree.leaves()]

        flag = False        #shows whether intent is find or not
        if len(series):
            tree.draw()
            verbs = [w for w, pos in series if re.match(r'VB.?', pos) is not None]
            nouns = [w for w, pos in series if re.match(r'NN.?', pos) is not None]
            print('verbs', verbs)
            print('nouns', nouns)
            if len(verbs):
                lemma = WordNetLemmatizer()
                L = [lemma.lemmatize(i, pos='v') for i in verbs if lemma.lemmatize(i, pos='v') not in stopWords]
                if len(L) : self.intent = L

            if len(nouns):
                if len(verbs):
                    pos1 = self.find_pos(verbs[0])
                    pos2 = self.find_pos(nouns[0])
                    if pos1 < pos2:
                        self.action_upon = nouns
                    else :
                        self.discardedNouns.append(nouns[0])
                        print(self.discardedNouns)

        if len(obj) and (self.intent is False or self.action_upon is False):
            tree.draw()
            verbs = [w for w, pos in obj if re.match(r'VB.?', pos) is not None]
            nouns = [w for w, pos in obj if re.match(r'NN.?', pos) is not None]
            print('verbs1', verbs)
            print('nouns1', nouns)
            if len(verbs) and self.intent is False:
                lemma = WordNetLemmatizer()
                L = [lemma.lemmatize(i, pos='v') for i in verbs if i not in self.discardedVerbs and lemma.lemmatize(i, pos='v') not in stopWords]
                print('L1',L)
                print('stopWords',stopWords)
                if len(L) : self.intent = L

            elif len(nouns) and self.intent is False:
                L = self.filterOutVerbs(nouns)
                if len(L):
                    for i in L : self.discardedNouns.append(i)
                    self.intent = L

            if len(nouns) and self.action_upon is False:
                self.action_upon = nouns

        #if no intent is found yet then below
        if  self.intent is False:
            print('1')
            tree = self.get_POS_tree(chunkGramForOnlyVerb)
            tree.draw()
            verbs = []
            verbs.clear()
            for subtree in tree.subtrees(filter=lambda t: t.label() == 'VR'):
                verbs = verbs + [s for s in subtree.leaves()]

            print('verbs',verbs)
            if len(verbs):
                 L = [w for w,pos in verbs]
                 L = self.filterOutVerbs(L)
                 if len(L):
                     self.intent = L
                     flag = True

        print(self.discardedNouns)
        if self.action_upon is not False:
            self.action_upon = [i for i in self.action_upon if i not in self.discardedNouns]

        L = self.get_attributes()
        if len(L):
            self.attributes = L

        if self.intent is False or len(self.intent)==0:
            self.intent = ['No Intent Found']

        if self.action_upon is False:
            self.action_upon = ['No Action Found']
        if self.attributes is False:
            self.attributes = ['No Attribute(s) Found']

        return {
            'intent': ' , '.join(self.intent),
            'action_on' : ' , '.join(self.action_upon),
            'attributes': ' , '.join(self.attributes)
        }

    def get_attributes(self):
        adj = [w for w,pos in self.get_POS() if re.match(r'(JJ.?)', pos) is not None]
        return list(set(adj))

    def check(self):
        with open('sentences.txt', 'r') as f:
            lines = f.readlines()
        for line in lines:
            pass

    def get_similarity(self,w1,w2):
        w1 = wordnet.synsets(w1)
        w2 = wordnet.synsets(w2)
        return w1[0].wup_similarity(w2[0])

text ='I had ordered a warm pizza, but when delivered is already cold'

nlp = task(text,preprocessing=True)


print(nlp.get_POS())
all = nlp.get_intent()
print('\n')
print('Intent : ',all['intent'])
print('Action_on : ',all['action_on'])
print('Attributes : ',all['attributes'])


#I want to explore worlds beyond hoerizons'
