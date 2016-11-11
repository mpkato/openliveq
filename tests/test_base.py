from openliveq.__main__ import main
from openliveq.db import DBPATH
from click.testing import CliRunner
import os
import pytest
import openliveq as olq
from openliveq.db import SessionContextFactory

class TestBase(object):
    @classmethod
    def setup_class(cls):
        if os.path.exists(DBPATH):
            os.remove(DBPATH)
        runner = CliRunner()
        result = runner.invoke(main, ['load',
            os.path.join(os.path.dirname(__file__), "fixtures",
            "sample_questions.tsv"),
            os.path.join(os.path.dirname(__file__), "fixtures",
            "sample_clickthrough.tsv"),
            ])
        assert result.exit_code == 0

    @classmethod
    def teardown_class(cls):
        if os.path.exists(DBPATH):
            os.remove(DBPATH)

    @pytest.fixture
    def queries(self):
        filepath = os.path.join(os.path.dirname(__file__), "fixtures",
            "sample_queries.tsv")
        with open(filepath) as f:
            result = olq.Query.load(f)
        return result

    @pytest.fixture
    def questions(self):
        scf = SessionContextFactory()
        with scf.create() as session:
            result = session.query(olq.Question).all()
        return result

