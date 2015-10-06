# POS.py
# Builds a unigram tagger and a few methods for finding nouns
# attribute .cfd and method .

import nltk

class POS(object):

	def __init__(self):
		brown_tagged = nltk.corpus.brown.tagged_words()
		self.cfd = nltk.ConditionalFreqDist(brown_tagged)

	def percent_noun(self,word):
		fd = dict(self.cfd[word])
		if 'NNS' in fd and 'NN' in fd:
			return (fd['NN'] + fd['NNS'])/float(sum(fd.values()))
		elif 'NNS' in fd and 'NN' not in fd:
			return fd['NNS']/float(sum(fd.values()))
		elif 'NN' in fd and 'NNS' not in fd:
			return fd['NN']/float(sum(fd.values()))
		else:
			return 0 #????