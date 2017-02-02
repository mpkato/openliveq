from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from datetime import datetime
from .db import Base

class Question(Base):
    __tablename__ = 'questions'
    __table_args__ = (
        Index('questions_query_id_index', "query_id"),
        Index('questions_question_id_index', "question_id"),
        Index('questions_query_id_question_id_index', "query_id", "question_id"),
        )

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
            raise RuntimeError("Invalid format for %s: %s"
                % (cls.__name__, line))
        args = {attr: ls[i] for i, attr in enumerate(cls.ORDERED_ATTRS)}
        result = Question(**args)
        # convertion
        result.rank = int(result.rank)
        result.updated_at = datetime.strptime(result.updated_at,
            "%Y/%m/%d %H:%M:%S")
        result.answer_num = int(result.answer_num)
        result.view_num = int(result.view_num)

        return result
