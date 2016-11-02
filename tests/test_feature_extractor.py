# -*- coding: utf-8 -*-
import openliveq as olq
import pytest
import os

class TestFeatureExtractor(object):

    def test_parse_questions(self, fe, questions):
        result = fe.parse_questions(questions)
        assert result["1167627151"]["title"]["厚生"] == 2
        assert result["1167627151"]["title"]["共済年金"] == 1
        assert result["1167627151"]["title"]["有利"] == 1
        assert result["1167627151"]["title"]["期間"] == 1
        assert result["1167627151"]["snippet"]["合計"] == 1
        assert result["1167627151"]["question_body"]["国民年金"] == 2
        assert result["1167627151"]["best_answer_body"]["有利"] == 2

    def test_parse_queries(self, fe, queries):
        result = fe.parse_queries(queries)
        assert result["OLQ-9998"]["野球"] == 1
        assert len(result["OLQ-9998"]) == 1

    def test_count_doc_freq(self, fe, parsed_questions):
        result = fe.count_doc_freq(parsed_questions)
        assert result["社会保険事務所"] == 1
        assert result["国民年金"] == 8

    def test_count_collection_freq(self, fe, parsed_questions):
        result = fe.count_collection_freq(parsed_questions)
        assert result["社会保険事務所"] > 1
        assert result["国民年金"] > 8

    def test_extract(self, fe, queries, questions):
        result = fe.extract(queries, questions)
        assert len(result[0]["features"]) == len(fe.feature_names)
        assert len(result) == 5

    def test_feature_names(self, fe):
        names = fe.feature_names
        assert len(names) == len(fe.METHODS) * len(fe.FIELDS)\
            + len(fe.QUESTION_FEATURE_METHODS)

    @pytest.fixture
    def fe(self):
        return olq.FeatureExtractor()

    @pytest.fixture
    def question_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_questions.tsv")

    @pytest.fixture
    def query_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_queries.tsv")

    @pytest.fixture
    def questions(self, fe, question_filepath):
        with open(question_filepath) as f:
            result = olq.Question.load(f)
        return result

    @pytest.fixture
    def parsed_questions(self, fe, questions):
        result = fe.parse_questions(questions)
        return result

    @pytest.fixture
    def queries(self, fe, query_filepath):
        with open(query_filepath) as f:
            result = olq.Query.load(f)
        return result

    @pytest.fixture
    def parsed_queries(self, fe, queries):
        result = fe.parse_queries(queries)
        return result
