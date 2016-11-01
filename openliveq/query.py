class Query(object):

    def __init__(self, query_id, body):
        self.query_id = query_id
        self.body = body

    @classmethod
    def readline(cls, line):
        ls = [l.strip() for l in line.split("\t")]
        if len(ls) != 2:
            return None
        result = Query(*ls)
        return result

    @classmethod
    def load(cls, fp):
        result = []
        for line in fp:
            elem = Query.readline(line)
            result.append(elem)
        return result
