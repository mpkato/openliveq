import openliveq as olq
import pytest
import os

class TestRanklib(object):

    def test_init(self):
        rl = olq.Ranklib()

    def test_learn_file(self, rl, training_filepath):
        model = rl.learn_file(training_filepath)
        assert isinstance(model, bytes)

    def test_learn_file_fail(self, rl, training_filepath):
        import subprocess
        with pytest.raises(subprocess.CalledProcessError):
            rl.learn_file(training_filepath + ".")

    def test_score_file(self, rl, model, training_filepath):
        scores = rl.score_file(model, training_filepath)
        assert len(scores) == 13
        assert all([isinstance(s, float) for s in scores])

    @pytest.fixture
    def rl(self):
        return olq.Ranklib()

    @pytest.fixture
    def training_filepath(self):
        return os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_l2r.txt")

    @pytest.fixture
    def model(self, rl, training_filepath):
        return rl.learn_file(training_filepath)
