from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords as sw


class Reader(object):
    """Performs tokenization according to tokenization options."""

    def __init__(self, stopwords=False, hyphens=False, digits=True):

        self.hyphens = hyphens
        self.digits = digits
        self.stopwords = stopwords

        # build a regex according to options
        if hyphens:
            if digits:
                exp = r'[\w\-]+'
            else:
                exp = r'[A-ZA-Z\-]+'
        else:
            if digits:
                exp = r'\w+'
            else:
                exp = r'[A-Za-z]+'

        self.tokenizer = RegexpTokenizer(exp)

    def tokens(self, document):
        if type(document) == 'unicode':
            raw = unicode(document, errors='ignore')
        else:
            raw = document
        tokens = self.tokenizer.tokenize(raw.lower())

        if not self.stopwords:
            stop = sw.words('english')
            tokens = [word for word in tokens if word not in stop]

        return tokens
