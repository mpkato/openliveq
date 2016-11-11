class Instance(object):

    def __init__(self, query_id, question_id, features, grade=0):
        self.query_id = query_id
        self.question_id = question_id
        self.features = features
        self.grade = grade

    @classmethod
    def dump(cls, tmpqid, instances, fp):
        '''
        tmpqid: positive integer representing a query ID
        instances: ones that belongs to the same query
        '''
        assert len(set([i.query_id for i in instances])) == 1
        for i in instances:
            line = [str(i.grade), "qid:%s" % tmpqid]
            line += ["%s:%s" % (idx+1, f)
                for idx, f in enumerate(i.features)]
            line += ["#", i.query_id, i.question_id]
            fp.write(" ".join(line) + "\n")
