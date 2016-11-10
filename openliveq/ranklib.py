import os
import sys
import subprocess
import tempfile
from collections import defaultdict
from .instance import Instance

RANKLIB_FILEPATH = os.path.join(os.path.dirname(__file__), 'RankLib-2.1.jar')

class Ranklib(object):
    CMD = ["java", "-jar"]

    def __init__(self, filepath=RANKLIB_FILEPATH):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            raise IOError("%s not found")
        ret = self._exec([])
        if not ret.startswith("Usage: java -jar RankLib.jar"):
            raise IOError("%s is not valid")

    def learn(self, instances, **kwargs):
        learnfile = self._tempfile()
        instances = sorted(instances, key=lambda x: x.query_id)
        with open(learnfile, "w") as f:
            Instance.dump(instances, f)
        return self.learn_file(learnfile)

    def score(self, model, instances, **kwargs):
        testfile = self._tempfile()
        instances = sorted(instances, key=lambda x: x.query_id)
        with open(testfile, "w") as f:
            Instance.dump(instances, f)
        scores = self.score_file(model, testfile)

        result = defaultdict(list)
        for i, s in zip(instances, scores):
            result[i.query_id].append((i, s))
        for query_id in result:
            result[query_id] = sorted(result[query_id],
                key=lambda x: x[1], reverse=True)

        return result

    def learn_file(self, filepath, **kwargs):
        savefile = self._tempfile()
        params = ["-train", filepath, "-save", savefile]
        for op in kwargs.items():
            params += list(map(str, op))
        self._exec(params)

        with open(savefile, 'rb') as f:
            result = f.read()

        return result

    def score_file(self, model, filepath, **kwargs):
        savefile = self._tempfile()
        modelfile = self._tempfile()
        with open(modelfile, "wb") as f:
            f.write(model)
        params = ["-load", modelfile, "-rank", filepath, "-score", savefile]
        for op in kwargs.items():
            params += list(map(str, op))
        self._exec(params)

        result = []
        with open(savefile, 'r') as f:
            for line in f:
                ls = [l.strip() for l in line.split("\t")]
                result.append(float(ls[-1]))
        return result

    def _tempfile(self):
        tmp = tempfile.NamedTemporaryFile()
        tmp.close()
        return tmp.name

    def _exec(self, params):
        cmd = list(self.CMD) + [self.filepath] + params
        try:
            ret  =  subprocess.check_output(cmd)
            ret = ret.decode()
        except subprocess.CalledProcessError as e:
            print(e.stdout.decode(), file=sys.stderr)
            raise e
        return ret
