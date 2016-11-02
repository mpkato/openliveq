import openliveq as olq
from openliveq.features import (answer_num, log_answer_num,
    view_num, log_view_num, is_open, is_vote, is_solved, rank, updated_at)
import pytest
import os
from math import log

class TestQuestionFeatures(object):

    def test_answer_num(self, q1, q2):
        assert answer_num(q1) == 1
        assert answer_num(q2) == 2

    def test_view_num(self, q1, q2):
        assert view_num(q1) == 952
        assert view_num(q2) == 14593

    def test_is_open(self, q1, q2):
        assert is_open(q1) == 0
        assert is_open(q2) == 0

    def test_is_vote(self, q1, q2):
        assert is_vote(q1) == 0
        assert is_vote(q2) == 0

    def test_is_solved(self, q1, q2):
        assert is_solved(q1) == 1
        assert is_solved(q2) == 1

    def test_rank(self, q1, q2, q3):
        assert rank(q1) == 1
        assert rank(q2) == 1
        assert rank(q3) == 2

    def test_updated_at(self, q1, q2, q3):
        assert updated_at(q1) > updated_at(q2)
        assert updated_at(q2) > updated_at(q3)

    @pytest.fixture
    def fe(self):
        return olq.FeatureExtractor()

    @pytest.fixture
    def question_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_questions.tsv")

    @pytest.fixture
    def questions(self, fe, question_filepath):
        with open(question_filepath) as f:
            result = olq.Question.load(f)
        return result

    @pytest.fixture
    def q1(self, questions):
        return questions[0]

    @pytest.fixture
    def q2(self, questions):
        return questions[1]

    @pytest.fixture
    def q3(self, questions):
        return questions[2]
