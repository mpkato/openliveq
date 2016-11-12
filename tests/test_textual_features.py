import openliveq
from openliveq.features import (
    tf_sum, log_tf_sum, norm_tf_sum, log_norm_tf_sum, idf_sum, log_idf_sum,
    icf_sum, log_tfidf_sum, tfidf_sum, tf_in_idf_sum, bm25, log_bm25,
    lm_dir, lm_jm, lm_abs, dlen, log_dlen)
import pytest
from math import log

class TestTextualFeatures(object):

    def test_tf_sum(self, q, d, c):
        res = tf_sum(q, d, c)
        assert res == 4

    def test_norm_tf_sum(self, q, d, c):
        res = norm_tf_sum(q, d, c)
        assert res == 1
        res = norm_tf_sum(q, {}, c)
        assert res == 0

    def test_lm_dir(self, q, d, c):
        actual = log((1.0 + 50 * 3.0 / 15) / (4.0 + 50))\
            - log(50.0 / (4.0 + 50) * 3.0 / 15)\
            + log((3.0 + 50 * 7.0 / 15) / (4.0 + 50))\
            - log(50.0 / (4.0 + 50) * 7.0 / 15)\
            + 3 * log(50.0 / (4.0 + 50))\
            + log(3.0 / 15) + log(5.0 / 15) + log(7.0 / 15)
        result = lm_dir(q, d, c)
        assert actual == pytest.approx(result)

    def test_lm_jm(self, q, d, c):
        actual = log(0.5 * 1.0 / 4.0 + 0.5 * 3.0 / 15)\
            - log(0.5 * 3.0 / 15)\
            + log(0.5 * 3.0 / 4.0 + 0.5 * 7.0 / 15)\
            - log(0.5 * 7.0 / 15)\
            + 3 * log(0.5)\
            + log(3.0 / 15) + log(5.0 / 15) + log(7.0 / 15)
        result = lm_jm(q, d, c)
        assert actual == pytest.approx(result)

    def test_lm_abs(self, q, d, c):
        actual = log(0.5 / 4.0 + 1.0 / 4.0 * 3.0 / 15)\
            - log(1.0 / 4.0 * 3.0 / 15)\
            + log(2.5 / 4.0 + 1.0 / 4.0 * 7.0 / 15)\
            - log(1.0 / 4.0 * 7.0 / 15)\
            + 3 * log(1.0 / 4.0)\
            + log(3.0 / 15) + log(5.0 / 15) + log(7.0 / 15)
        result = lm_abs(q, d, c)
        assert actual == pytest.approx(result)

    @pytest.fixture
    def q(self):
        return {"a": 1, "b": 1, "c": 1}

    @pytest.fixture
    def d(self):
        return {"a": 1, "c": 3}

    @pytest.fixture
    def c(self, parsed_questions):
        c = openliveq.Collection()
        c.add(parsed_questions["1"])
        return c

    @pytest.fixture
    def parsed_questions(self):
        return {"1": {"question_body": {"a": 1, "b": 2, "c": 3},
            "best_answer_body": {"a": 1, "b": 2, "c": 3}}}
