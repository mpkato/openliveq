from .nlp.parser import Parser
from .feature_factory import FeatureFactory
from .features import (
    # textual_features
    tf_sum, log_tf_sum, norm_tf_sum, log_norm_tf_sum, idf_sum, log_idf_sum,
    icf_sum, log_tfidf_sum, tfidf_sum, tf_in_idf_sum, bm25, log_bm25,
    lm_dir, lm_jm, lm_abs, dlen, log_dlen,
    # question_features
    answer_num, log_answer_num,
    view_num, log_view_num, is_open, is_vote, is_solved, rank, updated_at)
from collections import defaultdict

class FeatureExtractor(object):
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

    def extract(self, queries, questions):
        parsed_queries = self.parse_queries(queries)
        parsed_questions = self.parse_questions(questions)

        ff = FeatureFactory(parsed_questions)

        result = []
        for q in questions:
            f = self.extract_features(q,
                parsed_queries[q.query_id],
                parsed_questions[q.question_id],
                ff)
            result.append({"query_id": q.query_id,
                "question_id": q.question_id, "features": f})

        return result

    def extract_features(self, question,
            parsed_query, parsed_question, ff):
        result = []
        for field in self.FIELDS:
            result += [m(parsed_query, parsed_question[field], ff)
                for m in self.METHODS]
        for qf in self.QUESTION_FEATURE_METHODS:
            result.append(qf(question))
        return result

    def parse_questions(self, questions):
        result = {}
        for q in questions:
            txts = {}
            for l in self.FIELDS:
                txts[l] = getattr(q, l)
            wordsets = {l: self._to_dict(
                self.parser.content_word_tokenize(txt))
                for l, txt in txts.items()}
            result[q.question_id] = wordsets
        return result

    def parse_queries(self, queries):
        result = {}
        for q in queries:
            wordset = self._to_dict(
                self.parser.content_word_tokenize(q.body))
            result[q.query_id] = wordset
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

