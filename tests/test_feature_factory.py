import openliveq as olq
import pytest
import os

class TestFeatureFactory(object):
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
