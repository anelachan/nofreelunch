# Reader.py
# Performs tokenization
# Can access attributes .raw and .words

import nltk
from nltk.corpus import PlaintextCorpusReader
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

default_options = {
	'stopwords': False,
	'hyphens': False,
	'digits': True
}

class Reader(object):

	def __init__(self,document,options=default_options):
		# NECESSARY? if we pull direct from database, IT'S ALREADY UNICODE
		if type(document) == 'unicode':
			self.raw = unicode(document,errors='ignore')
		else:
			self.raw = document
		# set options
		self.options = default_options
		for key in options.keys():
			self.options[key] = options[key]

		if self.options['hyphens']:
			if self.options['digits']:
				exp = r'[\w\-]+'
			else:
				exp = r'[A-ZA-Z\-]+'
		else:
			if self.options['digits']:
				exp = r'\w+'
			else:
				exp = r'[A-Za-z]+'

		# tokenize
		tokenizer = RegexpTokenizer(exp)
		tokens = tokenizer.tokenize(self.raw.lower())

		if not self.options['stopwords']:
			stop = stopwords.words('english')
			tokens = [word for word in tokens if word not in stop]

		self.words = tokens