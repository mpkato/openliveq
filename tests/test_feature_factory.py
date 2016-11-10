import openliveq as olq
import pytest
import os
from .test_base import TestBase

class TestFeatureFactory(TestBase):
    def test_count_doc_freq(self, ff, parsed_questions):
        result = ff.count_doc_freq(parsed_questions)
        assert result["社会保険事務所"] == 1
        assert result["国民年金"] == 8

    def test_count_collection_freq(self, ff, parsed_questions):
        result = ff.count_collection_freq(parsed_questions)
        assert result["社会保険事務所"] > 1
        assert result["国民年金"] > 8

    @pytest.fixture
    def ff(self, parsed_questions):
        return olq.FeatureFactory(parsed_questions)

    @pytest.fixture
    def fe(self):
        return olq.FeatureExtractor()

    @pytest.fixture
    def parsed_questions(self, fe, questions):
        result = fe.parse_questions(questions)
        return result

    @pytest.fixture
    def parsed_queries(self, fe, queries):
        result = fe.parse_queries(queries)
        return result
