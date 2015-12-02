"""Extracts useful features from a volume of review text.
Handles tokenization and runs single word and phrasal extraction.
Needs modules Reader, UnigramFinder and PhraseFinder."""

import gc
import re
import nltk
import pandas as pd
from Reader import Reader
from UnigramFinder import UnigramFinder
from PhraseFinder import PhraseFinder


class FeatureExtraction(object):

    def __init__(self, db, num_unigrams=10, max_features=22):

        self.db = db
        self.num_unigrams = num_unigrams
        self.max_features = max_features
        self.features = None
        self.df = None

    def index(self, category):
        """Extract features and build an index of features in reviews"""
        # get all reviews from one product category
        reviews = self.reviews(self.db, category)
        reviews = self.parse_reviews(reviews)
        # join into 1 list of tokens
        tokens = self.join_review_tokens(reviews)
        features = self.extract_features(category, tokens)

        # record if feature string in review - indexing
        for obj in reviews:
            for feature in features:
                if feature.lower() in obj['review'].lower():
                    obj[feature] = True
                else:
                    obj[feature] = False
            # delete for some space saving
            del obj['bigrams']
            del obj['trigrams']
            del obj['tokens']
        gc.collect()

        # create review df
        df = pd.DataFrame(reviews)

        # prune those voted not helpful
        df['percent_helpful'] = df['helpful_votes'] / df['votes']
        df['percent_helpful'] = df['percent_helpful'].fillna(.5)
        mean_ph = df['percent_helpful'].mean()
        # update the list of features
        self.features = [feature for feature in features
                         if df[df[feature]]['percent_helpful'].mean()
                         > mean_ph]
        self.df = df

    def extract_features(self, category, tokens):
        # run unigram and phrasal feature extraction
        unigram_finder = UnigramFinder(category)
        phrase_finder = PhraseFinder()

        unigrams = unigram_finder.unigrams(tokens)[:self.num_unigrams]
        phrases = phrase_finder.phrases(tokens)

        # merge unigrams, bigrams and trigrams and flatten phrases
        all_frequent_features = self.merge(unigrams, phrases, category)

        # cap the list
        if len(all_frequent_features) > self.max_features:
            all_frequent_features = all_frequent_features[:self.max_features]

        return all_frequent_features

    def reviews(self, db, category):
        """Get reviews from database - return a list of dicts."""
        reviews = list(db.review.find({'category': category},
                       {'helpful_votes': 1,
                        'votes': 1,
                        'review': 1,
                        'stars': 1,
                        'product_id': 1}))
        return reviews

    def parse_reviews(self, reviews):
        # tokenize each review, add to each review obj IN PLACE
        for obj in reviews:
            obj['tokens'] = Reader().tokens(obj['review'])
            obj['bigrams'] = list(nltk.bigrams(obj['tokens']))
            obj['trigrams'] = list(nltk.trigrams(obj['tokens']))
        return reviews

    def join_review_tokens(self, reviews):
        """Concatenate the words for one product category together"""
        all_tokens = list()
        for obj in reviews:
            all_tokens += obj['tokens']
        return all_tokens

    def merge(self, unigrams, phrases, category):
        """Merge the unigrams and phrases."""
        # remove duplicate lemmas from unigrams
        unigrams = self.reduce_unigrams(unigrams)

        # turn the phrases into a set of single words
        phrase_words = set([word for phrase in phrases for word in phrase])
        # extra unigrams are those not already contained in a phrase.
        extra_unigrams = set(unigrams) - phrase_words

        # turn phrases into strings incl. stopwords
        joined_phrases = self.rebuild_phrases(phrases, category)

        # combine single words and phrases
        all_frequent_features = joined_phrases + list(extra_unigrams)
        return all_frequent_features

    def reduce_unigrams(self, unigrams):
        """Remove duplicate lemmas from Unigrams. WARNING CHANGES IN PLACE.
        Keep plurals - we want batteries not 'battery'"""
        wnl = nltk.WordNetLemmatizer()
        lemmas = [wnl.lemmatize(word) for word in unigrams]
        lemma_counts = nltk.FreqDist(lemmas)
        for word in lemma_counts.keys():
            if lemma_counts[word] > 1:
                # just remove the first one
                first = lemmas.index(word)
                del unigrams[first]
        return unigrams

    def rebuild_phrases(self, phrases, category):
        """Put the stopwords and special characters back into the phrases
        which may have been lost during tokenization."""

        joined = []
        # loop through phrases looking for stopwords or special characters
        for phrase in phrases:
            # not an abbreviation
            if len(phrase[0]) != 1:
                regex_str = '.{0,10}'.join(phrase)
            # an abbrevation w/ something in the middle
            else:
                regex_str = '[^\w]'.join(phrase)

            pattern = re.compile(regex_str, re.IGNORECASE)
            matches = list(self.db.review.find(
                {'category': category, 'review': {'$regex': pattern}}))

            review_strs = []
            for el in matches:
                try:
                    review_strs.append(re.search('(' + regex_str + ')',
                                       el['review'], re.IGNORECASE).group(1))
                except AttributeError:
                    pass

            # take most frequently said phrase
            fd = dict(nltk.FreqDist(review_strs))
            most_popular = sorted(fd.keys(), key=fd.get)[-1]
            joined.append(most_popular)

        return joined
