# FeatureExtraction.py
# Extractions useful features from a volume of review text
# Handles tokenization and runs single word and phrasal extraction.
# Depends on modules Reader, UnigramFinder and PhraseFinder.

from Reader import *
from UnigramFinder import *
from PhraseFinder import *
import re
import nltk
import gc
import pandas as pd # i think we can remove this

class FeatureExtraction(object):

	def __init__(self,category,db):

		self.db = db
		self.category = category

		reviews = list(self.db.review.find({'category': category},
			{'helpful_votes':1,'votes': 1,'review':1,'stars':1,'product_id':1}))

		# tokenize each review, add to review obj
		for obj in reviews:
			obj['tokens'] = Reader(obj['review']).words
			obj['bigrams'] = list(nltk.bigrams(obj['tokens']))
			obj['trigrams'] = list(nltk.trigrams(obj['tokens']))

		# concatenate the words together
		words = list()
		for obj in reviews:
			words += obj['tokens']

		# run unigram and phrasal feature extraction
		unigrams = UnigramFinder(words,category).unigrams[:15]
		phrases = PhraseFinder(words).phrases

		# remove duplicates singular-plural, BUT KEEP PLURALS.
		# i.e. we want 'batteries' not the lemma 'battery'
		wnl = nltk.WordNetLemmatizer()
		lemmas = [wnl.lemmatize(word) for word in unigrams]
		lemma_counts = nltk.FreqDist(lemmas)
		for word in lemma_counts.keys():
			if lemma_counts[word] > 1:
				# just remove the first one
				i1 = lemmas.index(word)
				del unigrams[i1]

		# merge the unigrams and phrases
		phrase_words = set([word for phrase in phrases for word in phrase])
		extra_unigrams = set(unigrams) - phrase_words

		# turn phrases into strings incl. stopwords
		joined_phrases = self.match_phrases(phrases)
		all_frequent = joined_phrases + list(extra_unigrams)
		self.all_frequent = all_frequent
		if len(all_frequent) > 22:
			all_frequent = all_frequent[:22]

		# record if feature string in review - indexing
		for obj in reviews:
			for feature in all_frequent:
				if feature.lower() in obj['review'].lower(): # ignore case
					obj[feature] = True
				else:
					obj[feature] = False
			del obj['bigrams']
			del obj['trigrams']
			del obj['tokens']

		# delete for some space saving
		gc.collect()

		# create review df
		df = pd.DataFrame(reviews)
		self.meaningful = all_frequent

		# prune for 'not helpful'
		df['percent_helpful'] = df['helpful_votes']/df['votes']
		df['percent_helpful'] = df['percent_helpful'].fillna(.5)
		mean_ph = df['percent_helpful'].mean()
		self.meaningful = [feature for feature in all_frequent 
			if df[df[feature]]['percent_helpful'].mean() > mean_ph]
		self.df = df

	# LOOK FOR WILDCARDS
	def match_phrases(self,phrases):
		joined = []
		# loop through phrases attempting to find any stopwords or special characters
		for phrase in phrases:
			if len(phrase[0]) != 1: # not an abbreviation
				regex_str = '.{0,10}'.join(phrase)
			else: # an abbrevation w/ something in the middle
				regex_str = '[^\w]'.join(phrase)
			pattern = re.compile(regex_str,re.IGNORECASE)
			matches = list(self.db.review.find(
				{'category': self.category,
				'review': {'$regex': pattern}}))
			review_strs = []				
			for el in matches:
				try:
					review_strs.append(re.search('(' + regex_str + ')',
						el['review'],re.IGNORECASE).group(1))
				except AttributeError:
					pass
			# take most frequently said phrase
			fd = dict(nltk.FreqDist(review_strs))
			most_popular = sorted(fd.keys(),key=fd.get)[-1]
			joined.append(most_popular)
		return joined