# StarSentiment.py
# Scores products by feature, using human-supplied overall star rating
# Attribute .product_scores used in ProductScorer

import pandas as pd

class StarSentiment(object):

	# goal is to score each product by feature

	def __init__(self,category,db):

		self.db = db

		# pull from db
		reviews = list(self.db.review.find({'category': category}))
		products = list(self.db.product.find({'category': category},
			{'name':1, '_id': 1}))
		features = self.db.productcategory.find_one({'name': category})['features']

		# put in pandas and merge 
		review_df = pd.DataFrame(reviews,columns=reviews[0].keys())
		product_df = pd.DataFrame(products,columns=products[0].keys())
		df = pd.merge(review_df,product_df,left_on='product_id',right_on='_id')

		# build a dataframe of avg. rating for each feature, grouping by product
		stars = pd.DataFrame()
		for f in features:
			pt = df[df[f]][['name','stars']].pivot_table(index=['name'])
			stars = stars.join(pt,how='outer',rsuffix=('_'+f))
		stars.columns = features

		product_df['_id'] = product_df['_id'].apply(lambda x: str(x))
		self.product_scores = stars