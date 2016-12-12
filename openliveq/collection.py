from collections import defaultdict

class Collection(object):
    DOC_FROM = ["question_body", "best_answer_body"]

    def __init__(self):
        '''
        Compute the following statistics
        df: document frequency
        cf: collection frequency
        dn: total number of documents
        cn: total number of words
        '''
        self.df = defaultdict(int)
        self.cf = defaultdict(int)
        self.dn = 0
        self.cn = 0

    def add(self, wordsets):
        '''
        Add a question
        '''
        for label in self.DOC_FROM:
            for w in set(wordsets[label].keys()):
                self.df[w] += 1
                self.cf[w] += wordsets[label][w]
                self.cn += wordsets[label][w]
        self.dn += 1

    @property
    def avgdlen(self):
        return float(self.cn) / self.dn
