'''below code is written in python 3.6'''

import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import verbnet
from nltk.corpus import wordnet

stopWords = nltk.corpus.stopwords.words('english')
stopWords.append('go')

#list of coomon verbs to be discarded
discardedVerbs = ['want', 'give','ask','take','like','become']


class task:
    def __init__(self, text, **kwargs):
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
        return nltk.pos_tag(self.get_tokens())

    def preprocessing(self):
        '''
            Preprocessing on the text
            1 : remove the any unwanted character
            2 : lemmatize the word
        '''
        self.text = re.sub('[^A-Za-z0-9 -/\']', '', self.text)  # removes everything except alnum, space, single quotes
        L = self.get_tokens()
        lemma = WordNetLemmatizer()
        L = [lemma.lemmatize(i) for i in L]
        self.text = ' '.join(L)

    def filterOutVerbs(self, A):
        '''
            return the words :
            1 - which are in Wordnet's Verb
            2 - which are not the stopwords

        '''
        L = A[:]
        lemma = WordNetLemmatizer()
        L = [lemma.lemmatize(i, pos='v') for i in L]
        L = [i for i in L if i in verbnet.lemmas() and i not in stopWords]
        L = list(set(L))
        return L

    def get_POS_tree(self, chunk):
        return nltk.RegexpParser(chunk).parse(self.get_POS())

    def find_pos(self, w):
        tokens = self.get_tokens()
        for i in range(len(tokens)):
            if tokens[i] == w:
                return i
        else:
            return -1

    def get_all(self):
        '''
            This function return intent, action_on and attributs of the sentence
        '''

        chunkGramForNounVerb = r'''NV: {<VB.?>+<.*>*<NN.?>+ | <NN.?>+<.*>*<VB.?>+}  #chunking noun verbs
                            }<[^(VB|NN)].*|VBZ|>{       #chinking all except POS starting with VB or NN and VBZ'''

        chunkGramForOnlyVerb = r'''VR: {<VB.?>}
                            }<VBP|VBZ>+{'''

        tree = self.get_POS_tree(chunkGramForNounVerb)
        obj = []
        series = []
        L = []

        for subtree in tree.subtrees(filter=lambda t: t.label() == 'NV'):
            if len(subtree.leaves()) > 1:
                series = subtree.leaves()
            obj = obj + [s for s in subtree.leaves()]

        #working below, if tree got some pairs as subtree
        if len(series) and (self.intent is False or self.action_upon is False):
            #tree.draw()
            verbs = [w for w, pos in series if re.match(r'VB.?', pos) is not None]
            nouns = [w for w, pos in series if re.match(r'NN.?', pos) is not None]
            if len(verbs):
                L = self.filterOutVerbs(verbs)
                #discarding the unwanted verbs
                L = [i for i in L if i not in discardedVerbs]
                if len(L): self.intent = L

            if len(nouns):
                lemma = WordNetLemmatizer()
                # considering those nouns which do not act as a verb
                L = [i for i in nouns if i not in stopWords and lemma.lemmatize(i, pos='v') not in verbnet.lemmas()]
                if len(L): self.action_upon = L

        #below works, if intent or action_upon did nt found yet
        if len(obj) and (self.intent is False or self.action_upon is False):
            #tree.draw()
            verbs = [w for w, pos in obj if re.match(r'VB.?', pos) is not None]
            nouns = [w for w, pos in obj if re.match(r'NN.?', pos) is not None]
            if len(verbs) and self.intent is False:
                L = self.filterOutVerbs(verbs)
                #again removing the unwanted verbs
                L = [i for i in L if i not in discardedVerbs]
                if len(L): self.intent = L

            if len(nouns) and self.intent is False:
                #filtering out nouns which are verbs
                L = self.filterOutVerbs(nouns)
                if len(L):
                    #adding noun in discardedNouns which are verbs and present as intent
                    for i in L: self.discardedNouns.append(i)
                    self.intent = L

            if len(nouns) and self.action_upon is False:
                self.action_upon = nouns

        # if no intent is found yet then below
        if self.intent is False:
            print('3')
            tree = self.get_POS_tree(chunkGramForOnlyVerb)
            #tree.draw()
            verbs = []
            verbs.clear()
            for subtree in tree.subtrees(filter=lambda t: t.label() == 'VR'):
                verbs = verbs + [s for s in subtree.leaves()]

            if len(verbs):
                L = [w for w, pos in verbs]
                L = self.filterOutVerbs(L)
                if len(L):
                    self.intent = L

        if self.action_upon is not False:
            #again discarding nouns which are present as intent
            self.action_upon = [i for i in self.action_upon if i not in self.discardedNouns]

        L = self.get_attributes()

        if len(L):
            self.attributes = L

        if self.intent is False or len(self.intent) == 0:
            self.intent = ['No Intent Found']

        if self.action_upon is False:
            self.action_upon = ['No Action Found']
        if self.attributes is False:
            self.attributes = ['No Attribute(s) Found']

        return {
            'intent': ' , '.join(self.intent),
            'action_on': ' , '.join(self.action_upon),
            'attributes': ' , '.join(self.attributes)
        }

    def get_attributes(self):
        adj = [w for w, pos in self.get_POS() if re.match(r'(JJ.?)', pos) is not None]
        return list(set(adj))


text = 'show me the menu'

nlp = task(text, preprocessing=True)

print(nlp.get_POS())
all = nlp.get_all()
print('\n')
print('Intent : ', all['intent'])
print('Action_on : ', all['action_on'])
print('Attributes : ', all['attributes'])