# UnigramFinder.py
# Finds 'interesting' unigrams from tokens. To be interesting:
# - is typically a noun according to a tagged 'typical' corpus
# - is frequently mentioned in review corpus
# - is less frequently mentioned in a 'generic' corpus
# Unigram object attribute .unigrams is used by FeatureExtraction.

import nltk
import pandas as pd
import numpy as np
from POS import POS

class UnigramFinder(object):

	def __init__(self,tokens,category):

		# these generic words will be ignored
		stopwords = ['product','price','reviews','unit','model',
		'purchase','amount','item']
		words = category.split()
		# add the category and its plural (crude) to stopwords
		for el in words:
			stopwords.append(el)
			stopwords.append(el+'s')

		# will have to change this!
		self.tokens = tokens
		self.num_words = len(self.tokens)

		# calculate freq dist from tokens
		self.unigram_fd = nltk.FreqDist(self.tokens)
		self.unique_words = len(self.unigram_fd)

		# get frequent unigram nouns
		pos = POS()
		common_unigrams = self.unigram_fd.most_common(int(.02*self.unique_words))
		self.unigrams = [pair for pair in common_unigrams \
			if pair[0] not in stopwords and pos.percent_noun(pair[0]) > 0.5]

		# use threshold? get slightly better w/o the threshold.
		# threshold = .001
		# self.unigrams = [pair for pair in common_unigrams \
		# 	if pair[1] > int(threshold*self.num_words) and pair[0] not in stopwords 
		# 	and pos.percent_noun(pair[0]) > 0.5]

		# create a pandas DataFrame indexed by word, review corpus
		zipped = zip(*self.unigrams)
		df_reviews = pd.DataFrame(list(zipped[1]),index=list(zipped[0]),
			columns=['count_reviews'])

		# a list of words from 'generic' corpus
		generic_words = self.chat_words()

		# create a pandas DataFrame indexed by word, generic
		self.generic_words = [w.lower() for w in generic_words]
		generic_fd = nltk.FreqDist(generic_words)+\
			nltk.FreqDist(nltk.bigrams(generic_words)) + \
			nltk.FreqDist(nltk.trigrams(generic_words))
		zipped_generic = zip(*generic_fd.items())
		df_generic = pd.DataFrame(list(zipped_generic[1]),\
			index=list(zipped_generic[0]),columns=['count_generic'])

		# merge the two on words
		df = df_reviews.join(df_generic)
		self.df = df.fillna(0)

		# compute generic freq.
		term_freq = self.term_freq_log()
		inverse_generic_freq = self.inverse_generic_freq()

		self.scores = term_freq * inverse_generic_freq
		self.scores.sort()
		self.unigrams = list(reversed(self.scores.index))

	def chat_words(self):
		return nltk.corpus.nps_chat.words()

	def chat_news_words(self):
		return nltk.corpus.nps_chat.words() +\
		 nltk.corpus.brown.words(categories='reviews')

	def term_freq(self):
		return self.df['count_reviews']

	def term_freq_log(self):
		return self.df['count_reviews'].apply(lambda x: (1+ np.log(x)))

	def inverse_generic_freq(self):
		return self.df['count_generic'].apply(lambda x: len(self.generic_words)/(x+1))

	def inverse_generic_freq_log(self):
		return self.df['count_generic'].apply(
			lambda x: np.log(len(self.generic_words)/(x+1)))

	def print_top_scores(self,num):
		print self.scores[-num:]

	def print_scores_threshold(self,threshold):
		print self.scores[self.scores > threshold]
