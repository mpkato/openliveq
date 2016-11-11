class QueryQuestion(object):

    def __init__(self, query_id, question_id):
        self.query_id = query_id
        self.question_id = question_id

    @classmethod
    def readline(cls, line):
        ls = [l.strip() for l in line.split("\t")]
        if len(ls) != 2:
            raise RuntimeError("Invalid format for %s: %s"
                % (cls.__name__, line))
        result = QueryQuestion(*ls)
        return result

    @classmethod
    def load(cls, fp):
        result = []
        for line in fp:
            elem = QueryQuestion.readline(line)
            result.append(elem)
        return result
