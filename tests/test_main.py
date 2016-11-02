from openliveq.__main__ import main
from click.testing import CliRunner
import pytest
import tempfile
import os

class TestMain(object):

    def test_main(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert result.output.startswith('Usage:')

        result = runner.invoke(main, ['nosuchcommand'])
        assert result.exit_code == 2
        assert result.output.startswith('Usage:')

    def test_feature_extraction(self, query_filepath, question_filepath):
        runner = CliRunner()
        result = runner.invoke(main, ["feature"])
        assert result.exit_code == 2
        assert result.output.startswith('Usage:')
        assert "Missing" in result.output

        output = tempfile.NamedTemporaryFile()
        filename = output.name
        output.close()
        result = runner.invoke(main, ["feature", 
            query_filepath, question_filepath, filename])
        assert result.exit_code == 0
        with open(filename) as f:
            lines = f.readlines()
        assert lines[0].startswith("OLQ-9998")
        assert lines[1].startswith("OLQ-9999")
        assert lines[2].startswith("OLQ-9999")
        assert lines[3].startswith("OLQ-9999")
        assert lines[4].startswith("OLQ-9999")
        assert len(lines) == 5

    @pytest.fixture
    def question_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_questions.tsv")

    @pytest.fixture
    def query_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_queries.tsv")
