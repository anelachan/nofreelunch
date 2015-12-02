# ProductScorer.py 
# ProductScorer is the main class for handling text mining.
# It dispatches the featureextraction and sentimentscoring modules
# Currently defaults to using star ratings but can be passed options 
# of sentiment='dictionary' or sentiment='classifier'.
# Prequisites: data already downloaded from Amazon, or built from data/

from pymongo import MongoClient
from bson.objectid import ObjectId
from featureextraction.FeatureExtraction import FeatureExtraction
from sentimentscoring.StarSentiment import StarSentiment
from sentimentscoring.DictSentiment import DictSentiment
from sentimentscoring.ClassifierSentiment import ClassifierSentiment
import pandas as pd
import numpy as np

class ProductScorer(object):

	def __init__(self,category,sentiment='stars'):

		# connect to database
		client = MongoClient('localhost',27017)
		db = client['nofreelunch']

		# run feature extractor
		f = FeatureExtraction(db)
		f.index(category)
		extracted = f.features
		df = f.df

		# update database w/ indexing information
		for feature in extracted:
			# update each review if contains impt feature
			for rec in df.index:
				if df.loc[rec][feature]:
					db.review.update(
						{ '_id': ObjectId(df.loc[rec]['_id']) },
						{ '$set': { feature : True } } )
				else:
					db.review.update(
						{ '_id': ObjectId(df.loc[rec]['_id']) },
						{ '$set': { feature : False } } )					

		# update product category with list of features
		db.productcategory.update( 
			{ 'name': category },
			{'$set': { 'features': extracted } })

		# sentiment analysis will do scoring
		# <product, feature, sentiment>
		if sentiment == 'stars':
			s = StarSentiment(category,db)
		elif sentiment == 'dictionary':
			s = DictSentiment(category,db)
		elif sentiment == 'classifier':
			s = ClassifierSentiment(category,db)
		product_scores = s.product_scores

		# update the product collection w/ scores
		for product in product_scores.index:
			for feature in product_scores.columns:
				rating = product_scores.loc[product][feature]
				if pd.isnull(rating):
					db.product.update({'name': product},{'$set': {feature: None}})
				else:
					db.product.update({'name': product},{'$set': {feature: rating}})

		# mine correlations
		corr = product_scores.corr()
		corr = corr[corr != 1]
		interesting = corr[np.abs(corr) > np.abs(corr).mean()]

		pairs = []
		stacked = interesting.stack()
		for feature1 in stacked.index.levels[0]:
			for feature2 in stacked[feature1].index:
				if (feature2,feature1) not in set(pairs):
					pairs.append((feature1,feature2))

		# update the productcategory collection
		db.productcategory.update({'name': category},
			{'$set': {'interesting': pairs}})

		# scale prices and update
		products = list(db.product.find({'category': category}))
		product_df = pd.DataFrame(products)
		product_df['price_scaled'] = ((5*product_df['price'].max()
			- 4*product_df['price'] - product_df['price'].min())/
		(product_df['price'].max() - product_df['price'].min()))
		for p in product_df.to_dict('records'):
			db.product.update({'_id': p['_id']},
				{'$set': {'price_scaled': p['price_scaled']}})

		client.close()