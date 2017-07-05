-------Problem - 2 Documentation--------

The code is written in python' latest version 3.6 and uses the NLTK library for the solution.

Used MatplotLib module, for plotting the histogram/graph for stop word frequency
Used Counter from Collection module, to convert the List to respective frequencies directly
Use Pickle Module, to store and load the Languages' stopwords model/object into 'stopWords' variable

Pickled 'stopWords' variable contains the stop words with respective to their language.
Language' Stop words used here are ['English','German','Spanish',''French'].
We can modify the code for more languages(supported by NLTK Corpus) by simple tweak.

Idea behind to detect the language of the paragraph/sentence, is that, for each sentences pass its nltk.word_tokens()
to the loop which matches the stop Words present in the sentence to its respective language stop words using above
loaded model/object, and store these language specific stopwords in the respective language list.

To find the mostly used language in the sentence/paragraph, we just need to find the Language which got the maximum numbers
of stop words present in the sentence/paragraph.

Finally, to show stop word histogram for that detected language, i used the Counter() on the sentence' stop word list for that language,
which converts the list of words into the list of words with their frequencies.
then sorted this generated frequency list using the Bubble sort in decreasing order of their frequencies.
Then this sorted frequency list is used to show the Histogram for the Stop words frequency.

Above code works better for bigger sentence/paragraph than smaller one.
