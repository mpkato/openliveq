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

    def test_learn(self, rl, instances):
        model = rl.learn(instances)
        assert isinstance(model, bytes)

    def test_score(self, rl, instances):
        model = rl.learn(instances)
        scores = rl.score(model, instances)
        assert len(scores) == 1
        assert len(scores["1"]) == 3
        assert scores["1"][0][0].question_id == "D2"

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

    @pytest.fixture
    def instances(self):
        result = []
        result.append(olq.Instance("1", "D1", [0.5, 0.0], 0))
        result.append(olq.Instance("1", "D2", [0.5, 1.0], 1.0))
        result.append(olq.Instance("1", "D3", [0.5, 0.0], 0))
        return result
