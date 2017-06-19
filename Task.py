import nltk
from nltk.corpus import stopwords
from collections import Counter
import re
from nltk.stem import WordNetLemmatizer
stopWords = nltk.corpus.stopwords.words('english')
from nltk.corpus import verbnet

class task:
    def __init__(self,text,**kwargs):
        self.text = text.lower()
        self.raw = text.lower()
        if bool(kwargs) is True:
            if kwargs['preprocessing']:
                self.preprocessing()

    def get_tokens(self):
        return nltk.word_tokenize(self.text)

    def get_POS(self):
        return nltk.pos_tag(self.get_tokens())

    def preprocessing(self):
        self.text = re.sub('[^A-Za-z0-9 -/\']','',self.text)    #removes everything except alnum & space
        L = self.get_tokens()
        #L = [i for i in L if i not in stopWords]
        lemma = WordNetLemmatizer()
        L = [lemma.lemmatize(i) for i in L]
        self.text = ' '.join(L)

    def filterOut(self,L):
        L = list(set(L))
        lemma = WordNetLemmatizer()
        L = [lemma.lemmatize(i, pos='v') for i in L]
        print(L)
        print(verbnet.lemmas())
        L = [i for i in L if i in verbnet.lemmas() and i not in stopWords]
        L = list(set(L))
        return L

    def get_intent(self):
        L = []
        '''
        chunking the
            1: verbs Only
            2: Verbs followed by nouns, and chinking "DT|TO|IN|VBP|VBZ|PRP.?|RB|W.*|JJ.?|CD" POS 
        '''
        chunkGram = r'''NP: {<VB.?><.*>?<NN.?>+ | <VB.?>}
                            }<DT|TO|IN|VBP|VBZ|PRP.?|RB|W.*|JJ.?|CD>+{    '''
        chunkParser = nltk.RegexpParser(chunkGram)
        tree = chunkParser.parse(self.get_POS())
        tree.draw();
        obj = []
        verb = []
        for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
            #if subtree has 2 or more words then push to obj
            if len(subtree.leaves()) > 1:
                obj.append(subtree.leaves())
            #if subtree has 1 word then push to verb
            elif len(subtree.leaves()) == 1:
                verb.append(subtree.leaves())

        if len(obj):
            #taking consideration only for first subtree
            L = [w for w, pos in obj[0]]

        if len(L):
            L = self.filterOut(L)
            if len(L):    return 'Intent : '+' , '.join(L)
            else:
                #in case if there is no subtree of words grater than two, then we only consider the "Verbs" present in the sentence
                for v in verb:
                    L = L + [w for w, pos in v]
                L = self.filterOut(L)
                if len(L):    return 'Intent : '+' , '.join(L)
                else:   return 'Sorry, No Intent Found'
        else:
            return 'Sorry, No Intent Found'


nlp = task('I want to eat something',preprocessing=True)
print(nlp.get_intent())