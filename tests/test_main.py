from openliveq.__main__ import main
from click.testing import CliRunner
import pytest
import tempfile
import os
import openliveq as olq
from openliveq.db import DBPATH, SessionContextFactory

class TestMain(object):

    def setup_method(self, method):
        if os.path.exists(DBPATH):
            os.remove(DBPATH)

    def teardown_method(self, method):
        if os.path.exists(DBPATH):
            os.remove(DBPATH)

    def test_main(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert result.output.startswith('Usage:')

        result = runner.invoke(main, ['nosuchcommand'])
        assert result.exit_code == 2
        assert result.output.startswith('Usage:')

    def test_feature_extraction(self, query_filepath, question_filepath, 
        query_question_filepath, clickthrough_filepath):
        runner = CliRunner()
        result = runner.invoke(main, ["feature"])
        assert result.exit_code == 2
        assert result.output.startswith('Usage:')
        assert "Missing" in result.output

        result = runner.invoke(main, ["load", 
            question_filepath, clickthrough_filepath])
        assert result.exit_code == 0

        output = tempfile.NamedTemporaryFile()
        filename = output.name
        output.close()
        result = runner.invoke(main, ["feature",
            query_filepath, query_question_filepath, filename])
        assert result.exit_code == 0
        with open(filename) as f:
            lines = f.readlines()
        assert "OLQ-9998" in lines[0]
        assert "OLQ-9999" in lines[1]
        assert "OLQ-9999" in lines[2]
        assert "OLQ-9999" in lines[3]
        assert "1167627151" in lines[0]
        assert "1328077703" in lines[1]
        assert "1414846259" in lines[2]
        assert "1348120213" in lines[3]
        for line in lines:
            assert line.startswith("0")
            assert len(line.split(" ")) == 82
        assert len(lines) == 4

    def test_load(self, question_filepath, clickthrough_filepath):
        runner = CliRunner()
        result = runner.invoke(main, ["load"])
        assert result.exit_code == 2
        assert result.output.startswith('Usage:')
        assert "Missing" in result.output

        result = runner.invoke(main, ["load", 
            question_filepath, clickthrough_filepath])
        assert result.exit_code == 0

        scf = SessionContextFactory()
        with scf.create() as session:
            cnt = session.query(olq.Question).count()
            assert cnt == 5
            cnt = session.query(olq.Clickthrough).count()
            assert cnt == 5

    @pytest.fixture
    def query_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_queries.tsv")

    @pytest.fixture
    def question_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_questions.tsv")

    @pytest.fixture
    def query_question_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_query_question.tsv")

    @pytest.fixture
    def clickthrough_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_clickthrough.tsv")
