# Run this script to build the database from the data/ directory
# and run the text mining modules to analyze/aggregate the data
# Prerequisite: mongod server instance must already be running!

# If desired, can pass ProductScorer different sentiment options - line 35

from pymongo import MongoClient
from mining.ProductScorer import ProductScorer
import datetime
import json

categories = ['space heater','wireless printer','drill']

client = MongoClient('localhost',27017)
db = client['nofreelunch']

# some housekeeping
client.drop_database('nofreelunch')

for c in categories:
	print 'Building database for ' + c
	category = json.load(open('data/' + c + '.json'))
	db.productcategory.insert(category)

	products = json.load(open('data/' + c + ' product reviews.json'))
	for p in products:
		reviews = p.pop('reviews')
		product_id = db.product.insert(p)
		for r in reviews:
			r['product_id'] = product_id
			db.review.insert(r)

	print 'Performing text mining for ' + c
	# run the text mining
	# if desired, could pass ProductScorer additional options,
	# to use classifier, do ProductScorer(c,'classifier')
	# to use dictionary, do ProductScorer(c,'dictionary')
	p = ProductScorer(c) 

client.close()