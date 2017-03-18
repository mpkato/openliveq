from collections import defaultdict
import json

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
        words = set()
        for label in self.DOC_FROM:
            words = words | set(wordsets[label].keys())
            for w in set(wordsets[label].keys()):
                self.cf[w] += wordsets[label][w]
                self.cn += wordsets[label][w]
        for w in words:
            self.df[w] += 1
        self.dn += 1

    def dump(self, f):
        json.dump(self.to_json(), f)

    def to_json(self):
        return {'df': self.df, 'cf': self.cf, 'dn': self.dn, 'cn': self.cn}

    @classmethod
    def load(cls, f):
        data = json.load(f)
        collection = Collection()
        for key in data:
            setattr(collection, key, data[key])
        return collection

    @property
    def avgdlen(self):
        return float(self.cn) / self.dn
