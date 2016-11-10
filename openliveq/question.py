from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Question(Base):
    __tablename__ = 'questions'

    ORDERED_ATTRS = ["query_id", "rank", "question_id", "title", "snippet",
        "status", "updated_at", "answer_num", "view_num", "category",
        "question_body", "best_answer_body"]

    query_id = Column(String(8), primary_key=True)
    rank = Column(Integer)
    question_id = Column(String(12), primary_key=True)
    title = Column(String(255))
    snippet = Column(Text)
    status = Column(String(10))
    updated_at = Column(DateTime)
    answer_num = Column(Integer)
    view_num = Column(Integer)
    category = Column(String(255))
    question_body = Column(Text)
    best_answer_body = Column(Text)

    @classmethod
    def readline(cls, line):
        ls = [l.strip() for l in line.split("\t")]
        if len(ls) != 12:
            return None
        args = {attr: ls[i] for i, attr in enumerate(cls.ORDERED_ATTRS)}
        result = Question(**args)
        # convertion
        result.rank = int(result.rank)
        result.updated_at = datetime.strptime(result.updated_at,
            "%Y/%m/%d %H:%M:%S")
        result.answer_num = int(result.answer_num)
        result.view_num = int(result.view_num)

        return result

    @classmethod
    def load(cls, fp):
        result = []
        for line in fp:
            elem = Question.readline(line)
            result.append(elem)
        return result
