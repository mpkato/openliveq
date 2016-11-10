class Instance(object):

    def __init__(self, query_id, question_id, features, grade=0):
        self.query_id = query_id
        self.questioin_id = question_id
        self.features = features
        self.grade = grade

    @classmethod
    def dump(cls, instances, fp):
        qids = {qid: idx+1 for idx, qid
            in enumerate(sorted(list(set([i.query_id for i in instances]))))}
        instances = sorted(instances, key=lambda x: x.query_id)
        for i in instances:
            qid = qids[i.query_id]
            line = [str(self.grade), "qid:%s" % qid]
            line += ["%s:%s" % (idx+1, f)
                for idx, f in enumerate(self.features)]
            line += ["#", self.query_id, self.question_id]
            fp.write(" ".join(line) + "\n")
