# ClassifierSentiment.py
# Classifies sentiment as positive/negative based on supervised learning.
# Training data is Hu and Liu product review dataset (included in huliu/)
# Uses a Naive Bayes classifier with TFIDF weights.
# Outputs a dataframe or products by feature scores.
# Attribute .product_scores used in ProductScorer

from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import nltk
import re
import os

# change this if runniing ClassifierSentiment on its own
HULIUDIR = 'sentimentscoring/huliu/' 

class ClassifierSentiment(object):

	def __init__(self,category,db):

		self.db = db
		self.category = category

		# train classifier
		self.tfidf_vect = TfidfVectorizer()
		self.train_classifier()

		# set up for 'test' sentences
		self.new_tfidf = TfidfVectorizer(vocabulary=self.tfidf_vect.vocabulary_)

		# setup scoring
		self.features = self.db.productcategory.find_one(
			{'name': category})['features']
		self.reviews = list(self.db.review.find({'category': category}))
		self.all_scores = [] # keep track of all the scores

		# go through each review and score by feature
		self.score_reviews()
		self.product_scores = self.build_product_scores()

	def train_classifier(self):
		sentences, y_train = self.build_train()
		X_train = self.tfidf_vect.fit_transform(sentences)
		
		self.classifier = MultinomialNB()
		self.classifier.fit(X_train,y_train)

	def build_train(self):
		files = [f for f in list(os.walk(HULIUDIR,topdown=True))[0][2] \
			if not f.startswith('.')]
		sentences = []
		scores = []

		for f in files:
			text = open(HULIUDIR +f).read()
			reviews = text.split('[t]')
			for review in reviews:
				feature_sentences = review.split('\n')[1:]
				for sentence in feature_sentences:
					data = sentence.split('##')
					if len(data) > 1:
						try:
							plusminus = re.search('\[(\+|-)(\d)\]',data[0]).group(1)
							if plusminus == '+':
								scores.append(1)
							if plusminus == '-':
								scores.append(0)
							sent = data[1]
							sentences.append(sent)
						except AttributeError:
							pass

		return (sentences, np.array(scores))

	def score_sentence(self,sentence):
		X_test = self.new_tfidf.fit_transform([sentence])
		return (self.classifier.predict_proba(X_test)[0][1] 
			- self.classifier.predict_proba(X_test)[0][0])

	def score_reviews(self):
		for obj in self.reviews:
			sentences = nltk.tokenize.sent_tokenize(obj['review'])
			for sent in sentences:
				for f in self.features:
					if obj[f]:
						if f.lower() in sent.lower():
							score = self.score_sentence(sent)
							obj[f] = score
							self.all_scores.append(score)

	def build_product_scores(self):
		# linearly map onto 1-5 scale 
		review_df = pd.DataFrame(self.reviews,columns=self.reviews[0].keys())
		review_df = review_df.replace(False,np.NaN)
		for f in self.features:
			review_df[f] = ((4*review_df[f] + review_df[f].max() 
				- 5*review_df[f].min())/(review_df[f].max()-review_df[f].min()))
		self.review_df = review_df

		# alternate method - discretize the scores, 
		# but according to ALL scores not each feature's
		# q, bins = pd.qcut(self.all_scores, 5, retbins=True)
		# bins = list(bins)
		# bins.append(2000)
		# review_df = pd.DataFrame(self.reviews,columns=self.reviews[0].keys())
		# review_df = review_df.replace(False,1000)
		# for f in self.features:
		# 	review_df[f] = pd.cut(review_df[f],bins,right=True).labels +1
		# review_df = review_df.replace(6,np.NaN)

		products = list(self.db.product.find({'category': self.category},
					{'name':1, '_id': 1}))
		product_df = pd.DataFrame(products,columns=products[0].keys())		
		df = pd.merge(review_df,product_df,left_on='product_id',right_on='_id')
		return df.pivot_table(index=['name'],values=self.features)