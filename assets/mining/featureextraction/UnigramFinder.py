import nltk
import pandas as pd
import numpy as np
from POS import POS


class UnigramFinder(object):

    """ Finds 'interesting' unigrams from tokens. To be interesting:
    - is typically a NOUN according to a tagged 'typical' corpus
    - is frequently mentioned in review corpus
    - is less frequently mentioned in a 'generic' corpus
    """

    def __init__(self, category, top_pct=.02):
        self.category = category
        self.top_pct = top_pct

    def unigrams(self, tokens):

        nouns = self.frequent_nouns_counts(tokens)
        review_word_counts = self.review_word_counts(nouns)
        generic_word_counts = self.generic_word_counts()

        # merge the two on words
        all_word_counts = review_word_counts.join(
            generic_word_counts).fillna(0)

        # compute tf and idf - use of log/not log was chosen by tuning
        term_freq = all_word_counts['count_reviews'].apply(
            lambda x: (1 + np.log(x)))

        inverse_generic_freq = all_word_counts['count_generic'].apply(
            lambda x: len(generic_word_counts) / (x + 1))

        scores = term_freq * inverse_generic_freq
        scores.sort(ascending=False)
        return list(scores.index)

    def frequent_nouns_counts(self, tokens):
        """Return frequently mentioned nouns WITH COUNTS"""

        unigram_fd = nltk.FreqDist(tokens)
        pos = POS()
        common_unigrams = unigram_fd.most_common(
            int(self.top_pct * len(unigram_fd)))

        nouns = [pair for pair in common_unigrams
                 if pair[0] not in self.stopwords()
                 and pos.percent_noun(pair[0]) > 0.5]

        return nouns

    def review_word_counts(self, noun_counts):
        """create a DataFrame of word counts, indexed by word"""
        zipped = zip(*noun_counts)
        words = list(zipped[0])
        counts = list(zipped[1])
        df_reviews = pd.DataFrame(counts, index=words,
                                  columns=['count_reviews'])
        return df_reviews

    def generic_word_counts(self):
        # a list of words from 'generic' corpus
        generic_words = nltk.corpus.nps_chat.words()

        # for the generic corpus: create a DataFrame indexed by word
        generic_words = [w.lower() for w in generic_words]
        generic_fd = (nltk.FreqDist(generic_words)
                      + nltk.FreqDist(nltk.bigrams(generic_words))
                      + nltk.FreqDist(nltk.trigrams(generic_words)))

        zipped = zip(*generic_fd.items())
        counts = list(zipped[1])
        words = list(zipped[0])

        df_generic = pd.DataFrame(counts, index=words,
                                  columns=['count_generic'])
        return df_generic

    def stopwords(self):
        # these generic words will be ignored
        stopwords = ['product', 'price', 'reviews', 'unit', 'model', 'use',
                     'purchase', 'amount', 'item']
        category_words = self.category.split()
        # add the category and its plural (crude) to stopwords
        for word in category_words:
            stopwords.append(word)
            stopwords.append(word + 's')

        return stopwords
