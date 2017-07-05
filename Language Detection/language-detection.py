import nltk
import matplotlib.pyplot as plt
from collections import Counter
import pickle

# loading the offline stopWords object/model via pickling
f = open('stopwords.pickle', 'rb')
stopWords = pickle.load(f)

class Task:
    def __init__(self, text, **kwargs):
        #lowercese all the text
        self.text = text.lower()
        #sent_tokenize() returns the list of all sentences
        self.sent = nltk.sent_tokenize(self.text)

    def get_tokens(self, s):
        '''
            retruns the sentence as tokens
        '''
        return nltk.word_tokenize(s)

    def sort_list(self,item):
        '''
            Sorting and returning the list containing (word, word Counts) tuples as it elements, using Bubble sort
        '''
        L = item[:]
        for i in range(len(L)):
            for j in range(len(L) - 1 - i):
                if L[j][1] < L[j+1][1]:
                    L[j], L[j + 1] = L[j + 1], L[j]
        return L

    def detect_language(self):
        '''
            this function creates a dictionay with its key => Language and value => stopWords,
            then returning that language which has got most number of the stopWords
        '''
        s = self.text
        lang_ids = stopWords.keys()

        # dic : dictionary, represents the language ant its stop words mapping
        dic = {i: [] for i in lang_ids}
        L = []
        for sent in self.sent:
            tokens = self.get_tokens(sent)
            for lang in lang_ids:
                L = [i for i in tokens if i in stopWords[lang]]
                if len(L):
                    dic[lang] += L

        max = 0
        detected_lang = False
        # below find the language which got most number of stop words
        for k,v in dic.items():
            if len(v) and len(v) > max:
                max = len(v)
                detected_lang = k

        if detected_lang is False:
            detected_lang = 'No Language detected'

        return detected_lang, dic[detected_lang]


    def get_all(self):
        '''
            this function creates a dictionay with its key => Language and value => stopWords,
            then returning that language which has got most number of the stopWords
        '''
        detected_lang, det_lang_stopWords = self.detect_language()
        print('Deteted language : ', detected_lang.title())

        # below sorts the detected language stopWords to their frequencies in form of (word,frequencies)
        det_lang_stopWords_freq = self.sort_list(list(Counter(det_lang_stopWords).items()))

        # below plots the stop words frequency graph for the detected_language
        v = det_lang_stopWords_freq
        x_str = [w for w, i in v]
        x_num = [i for i in range(len(x_str))]
        y = [i for w, i in v]
        plt.xticks(x_num, x_str, rotation=60)
        plt.yticks([i for i in range(1,max(y)+1)])
        plt.grid()
        plt.xlabel('Stop Words')
        plt.ylabel('Counts')
        plt.plot(x_num, y)
        plt.title('Stop words Histogram :\n')
        plt.show()



text = u'''Hamburg - Der Weltklimarat (IPCC) hat in Kopenhagen eine Debatte über die Zusammenfassung  aller drei Teile 
seines neuen großen Klimaberichts begonnen. Bis zum Freitag ringen  Wissenschaftler und Regierungsvertreter um 
den Wortlaut wichtiger Kernaussagen  des sogenannten Synthesis-Report, den Uno-Generalsekretär Ban Ki Moon 
und IPCC-Chef Rajendra Pachauri am Sonntag präsentieren wollen. Die drei einzelnen Teile des Reports hatte das 
Gremium im September  2013 sowie im März und April 2014 vorgestellt. Die neue Zusammenfassung solle ein 
Fahrplan für politische  Entscheidungsträger sein, anhand derer sie den Weg zu einem globalen Abkommen zum 
Klimaschutz finden könnten, sagte Pachauri am Montag zum Auftakt der Diskussionen in der dänischen Hauptstadt. Several mathematical operations are provided for combining Counter objects to produce multisets (counters that have counts greater than zero). Addition and subtraction combine counters by adding or subtracting the counts of corresponding elements. Intersection and union return the minimum and maximum of corresponding counts. Each operation can accept inputs with signed counts, but the output will exclude results with counts of zero or less.
 '''

nlp = Task(text)

nlp.get_all()

#Deteted language : German
