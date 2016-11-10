# -*- coding: utf-8 -*-
import openliveq as olq
import pytest
import os
from .test_base import TestBase
from openliveq.db import SessionContextFactory

class TestFeatureFactory(TestBase):

    def test_parse_questions(self, ff, questions):
        result = ff.parse_question(questions[0])
        assert result["title"]["厚生"] == 2
        assert result["title"]["共済年金"] == 1
        assert result["title"]["有利"] == 1
        assert result["title"]["期間"] == 1
        assert result["snippet"]["合計"] == 1
        assert result["question_body"]["国民年金"] == 2
        assert result["best_answer_body"]["有利"] == 2

    def test_parse_query(self, ff, queries):
        result = ff.parse_query(queries[0])
        assert result["野球"] == 1
        assert len(result) == 1

    def test_extract(self, ff, queries, questions, c):
        result = ff.extract(queries[0], questions[0], c)
        assert len(result.features) == len(ff.feature_names)

    def test_feature_names(self, ff):
        names = ff.feature_names
        assert len(names) == len(ff.METHODS) * len(ff.FIELDS)\
            + len(ff.QUESTION_FEATURE_METHODS)

    @pytest.fixture
    def ff(self):
        return olq.FeatureFactory()

    @pytest.fixture
    def c(self, parsed_questions):
        result = olq.Collection()
        for ws in parsed_questions:
            result.add(ws)
        return result

    @pytest.fixture
    def parsed_questions(self, ff, questions):
        result = []
        for q in questions:
            result.append(ff.parse_question(q))
        return result
