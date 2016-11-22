from .nlp.parser import Parser
from .instance import Instance
from .collection import Collection
from .features import (
    # textual_features
    tf_sum, log_tf_sum, norm_tf_sum, log_norm_tf_sum, idf_sum, log_idf_sum,
    icf_sum, log_tfidf_sum, tfidf_sum, tf_in_idf_sum, bm25, log_bm25,
    lm_dir, lm_jm, lm_abs, dlen, log_dlen,
    # question_features
    answer_num, log_answer_num,
    view_num, log_view_num, is_open, is_vote, is_solved, rank, updated_at)
from collections import defaultdict

class FeatureFactory(object):
    FIELDS = ["title", "snippet", "question_body", "best_answer_body"]
    METHODS = (
        tf_sum, log_tf_sum, norm_tf_sum, log_norm_tf_sum, idf_sum, log_idf_sum,
        icf_sum, log_tfidf_sum, tfidf_sum, tf_in_idf_sum, bm25, log_bm25,
        lm_dir, lm_jm, lm_abs, dlen, log_dlen)
    QUESTION_FEATURE_METHODS = (answer_num, log_answer_num,
        view_num, log_view_num, is_open, is_vote, is_solved,
        rank, updated_at)

    def __init__(self):
        self.parser = Parser()

    def extract(self, query, question, collection):
        p_query = self.parse_query(query)
        p_question = self.parse_question(question)
        assert query.query_id == question.query_id

        features = []
        for field in self.FIELDS:
            features += [m(p_query, p_question[field], collection)
                for m in self.METHODS]
        for qf in self.QUESTION_FEATURE_METHODS:
            features.append(qf(question))

        result = Instance(query.query_id, question.question_id, features)

        return result

    def parse_question(self, question):
        txts = {}
        for l in self.FIELDS:
            txts[l] = getattr(question, l)
        result = {l: self._to_dict(
            self.parser.content_word_tokenize(txt))
            for l, txt in txts.items()}
        return result

    def parse_query(self, query):
        result = self._to_dict(
            self.parser.content_word_tokenize(query.body))
        return result

    @property
    def feature_names(self):
        result = []
        for field in self.FIELDS:
            result += ["%s_%s" % (field, m.__name__)  for m in self.METHODS]
        for qf in self.QUESTION_FEATURE_METHODS:
            result.append(qf.__name__)
        return result

    def _to_dict(self, words):
        result = defaultdict(int)
        for w in words:
            result[w] += 1
        return result

