# PhraseFinder.py
# Extracts 'interesting' bigrams and trigrams from a long list of tokens. 
# Uses PMI scores with a frequency threshold.
# PhraseFinder object attribute .phrases used by FeatureExtraction.

from nltk.collocations import *
import nltk
from POS import POS

class PhraseFinder(object):

	def __init__(self,tokens):

		stopwords = set([('5','stars')])
		num_words = len(tokens)

		finder = BigramCollocationFinder.from_words(tokens)
		bigram_measures = nltk.collocations.BigramAssocMeasures()
		finder.apply_freq_filter(int(.0002*num_words)) # some parameter tunin?
		bigrams = finder.nbest(bigram_measures.pmi,15)

		tfinder = TrigramCollocationFinder.from_words(tokens)
		trigram_measures = nltk.collocations.TrigramAssocMeasures()
		tfinder.apply_freq_filter(int(.0001*num_words))
		trigrams = tfinder.nbest(trigram_measures.pmi,10)

		# merge bigrams and trigrams
		phrases = bigrams
		combined = []
		for bigram in bigrams:
			other_bigrams = list(set(bigrams) - set(bigram))
			for other_bigram in other_bigrams:
				if bigram[1] == other_bigram[0]:
					combined.append((bigram[0],bigram[1],other_bigram[1]))
		for trigram in trigrams:
			if trigram in set(combined):
				phrases.append(trigram)
				phrases.remove((trigram[0],trigram[1]))
				phrases.remove((trigram[1],trigram[2]))

		p = POS()
		self.phrases = [phrase for phrase in phrases 
			if p.percent_noun(phrase[-1]) > 0.5 and phrase not in stopwords]
