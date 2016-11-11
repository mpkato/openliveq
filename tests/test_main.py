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

    def test_feature_extraction(self, query_filepath, question_filepath):
        runner = CliRunner()
        result = runner.invoke(main, ["feature"])
        assert result.exit_code == 2
        assert result.output.startswith('Usage:')
        assert "Missing" in result.output

        result = runner.invoke(main, ["load", question_filepath])
        assert result.exit_code == 0

        output = tempfile.NamedTemporaryFile()
        filename = output.name
        output.close()
        result = runner.invoke(main, ["feature", query_filepath, filename])
        assert result.exit_code == 0
        with open(filename) as f:
            lines = f.readlines()
        assert "OLQ-9998" in lines[0]
        assert "OLQ-9999" in lines[1]
        assert "OLQ-9999" in lines[2]
        assert "OLQ-9999" in lines[3]
        assert "OLQ-9999" in lines[4]
        for line in lines:
            assert line.startswith("0")
            assert len(line.split(" ")) == 82
        assert len(lines) == 5

    def test_load(self, question_filepath):
        runner = CliRunner()
        result = runner.invoke(main, ["load"])
        assert result.exit_code == 2
        assert result.output.startswith('Usage:')
        assert "Missing" in result.output

        result = runner.invoke(main, ["load", question_filepath])
        assert result.exit_code == 0

        scf = SessionContextFactory()
        with scf.create() as session:
            cnt = session.query(olq.Question).count()
            assert cnt == 5

    @pytest.fixture
    def question_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_questions.tsv")

    @pytest.fixture
    def query_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_queries.tsv")
