import openliveq as olq
import pytest
import os
from .test_base import TestBase

class TestCollection(TestBase):
    def test_df(self, c):
        result = c.df
        assert result["社会保険事務所"] == 1
        assert result["国民年金"] == 4

    def test_cf(self, c):
        result = c.cf
        assert result["社会保険事務所"] > 1
        assert result["国民年金"] > 4

    @pytest.fixture
    def c(self, parsed_questions):
        result = olq.Collection()
        for ws in parsed_questions:
            result.add(ws)
        return result

    @pytest.fixture
    def ff(self):
        return olq.FeatureFactory()

    @pytest.fixture
    def parsed_questions(self, ff, questions):
        result = []
        for q in questions:
            result.append(ff.parse_question(q))
        return result
