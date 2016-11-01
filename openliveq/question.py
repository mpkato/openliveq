from datetime import datetime

class Question(object):

    def __init__(self, query_id, rank, question_id, title, snippet,
        status, updated_at, answer_num, view_num, category,
        question_body, best_answer_body):
        self.query_id = query_id
        self.rank = int(rank)
        self.question_id = question_id
        self.title = title
        self.snippet = snippet
        self.status = status
        self.updated_at = datetime.strptime(updated_at,
            "%Y/%m/%d %H:%M:%S")
        self.answer_num = int(answer_num)
        self.view_num = int(view_num)
        self.category = category
        self.question_body = question_body
        self.best_answer_body = best_answer_body

    @classmethod
    def readline(cls, line):
        ls = [l.strip() for l in line.split("\t")]
        if len(ls) != 12:
            return None
        result = Question(*ls)
        return result

    @classmethod
    def load(cls, fp):
        result = []
        for line in fp:
            elem = Question.readline(line)
            result.append(elem)
        return result
