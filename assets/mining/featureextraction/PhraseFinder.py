from nltk.collocations import (BigramCollocationFinder,
                               BigramAssocMeasures,
                               TrigramCollocationFinder,
                               TrigramAssocMeasures)
from POS import POS


class PhraseFinder(object):
    """" Extracts 'interesting' bigrams and trigrams from a list of tokens.
    Uses PMI scores with a frequency threshold."""

    def __init__(self, bigrams_pct_words=.0002, num_bigrams=15,
                 trigrams_pct_words=.0001, num_trigrams=10):

        self.bigrams_pct_words = bigrams_pct_words
        self.num_bigrams = num_bigrams
        self.trigrams_pct_words = trigrams_pct_words
        self.num_trigrams = num_trigrams

    def phrases(self, tokens):

        bigrams = self.top_bigrams(tokens)
        trigrams = self.top_trigrams(tokens)
        phrases = self.merged_phrases(bigrams, trigrams)

        # clean the phrases to be NOUN PHRASES and w/o phrasal stopwords.
        p = POS()
        stopwords = {('5', 'stars')}
        phrases = [phrase for phrase in phrases
                   if p.percent_noun(phrase[-1]) > 0.5
                   and phrase not in stopwords]

        return phrases

    def top_bigrams(self, tokens):
        finder = BigramCollocationFinder.from_words(tokens)
        bigram_measures = BigramAssocMeasures()
        finder.apply_freq_filter(int(self.bigrams_pct_words * len(tokens)))
        bigrams = finder.nbest(bigram_measures.pmi, self.num_bigrams)
        return bigrams

    def top_trigrams(self, tokens):
        tfinder = TrigramCollocationFinder.from_words(tokens)
        trigram_measures = TrigramAssocMeasures()
        tfinder.apply_freq_filter(int(self.trigrams_pct_words * len(tokens)))
        trigrams = tfinder.nbest(trigram_measures.pmi, self.num_trigrams)
        return trigrams

    def merged_phrases(self, bigrams, trigrams):
        """Merge bigrams and trigrams to remove trigrams made of bigrams."""
        # look for bigrams that connect to another bigram,
        # save the new tuple in a list called combined_phrases
        combined_phrases = []
        for bigram in bigrams:
            other_bigrams = list(set(bigrams) - set(bigram))
            for other_bigram in other_bigrams:
                if bigram[1] == other_bigram[0]:
                    trigram_tuple = (bigram[0], bigram[1], other_bigram[1])
                    combined_phrases.append(trigram_tuple)

        final_phrases = bigrams
        for trigram in trigrams:
            # if the trigram is already in the list of combined phrases
            if trigram in set(combined_phrases):
                # add it to the final phrase list
                final_phrases.append(trigram)
                # remove the redundant bigrams
                final_phrases.remove((trigram[0], trigram[1]))
                final_phrases.remove((trigram[1], trigram[2]))

        return final_phrases
