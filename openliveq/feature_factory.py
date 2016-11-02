from collections import defaultdict

class FeatureFactory(object):
    DOC_FROM = ["question_body", "best_answer_body"]

    def __init__(self, parsed_questions):
        '''
        Compute the following statistics
        df: document frequency
        cf: collection frequency
        dn: total number of documents
        cn: total number of words
        '''
        self.df = self.count_doc_freq(parsed_questions)
        self.cf = self.count_collection_freq(parsed_questions)
        self.dn = len(parsed_questions)
        self.cn = sum(self.cf.values())

    def count_doc_freq(self, question_wordsets):
        '''
        Document frequency based on DOC_FROM fields of questions
        '''
        result = defaultdict(int)
        for label in self.DOC_FROM:
            for question_id, wordsets in question_wordsets.items():
                for w in set(wordsets[label].keys()):
                    result[w] += 1
        return result

    def count_collection_freq(self, question_wordsets):
        '''
        Collection frequency based on DOC_FROM fields of questions
        '''
        result = defaultdict(int)
        for label in self.DOC_FROM:
            for question_id, wordsets in question_wordsets.items():
                for w in set(wordsets[label].keys()):
                    result[w] += wordsets[label][w]
        return result

