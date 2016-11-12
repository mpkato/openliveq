class Instance(object):

    def __init__(self, query_id, question_id, features, grade=0):
        self.query_id = query_id
        self.question_id = question_id
        self.features = features
        self.grade = grade

    @classmethod
    def dump(cls, tmpqid, instance, fp):
        '''
        tmpqid: positive integer representing a query ID
        '''
        line = [str(instance.grade), "qid:%s" % tmpqid]
        line += ["%s:%s" % (idx+1, f)
            for idx, f in enumerate(instance.features)]
        line += ["#", instance.query_id, instance.question_id]
        fp.write(" ".join(line) + "\n")
