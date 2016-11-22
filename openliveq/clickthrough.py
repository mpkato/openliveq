from sqlalchemy import Column, Integer, String, Float, Index
from .db import Base

class Clickthrough(Base):
    __tablename__ = 'clickthroughs'
    __table_args__ = (
        Index('clickthroughs_query_id_index', "query_id"),
        Index('clickthroughs_question_id_index', "question_id"),
        )

    ORDERED_ATTRS = [
        "query_id", "question_id", "rank", "ctr",
        "male", "female",
        "a00", "a10", "a20", "a30", "a40", "a50", "a60"]

    query_id = Column(String(8), primary_key=True)
    question_id = Column(String(12), primary_key=True)
    rank = Column(Integer)
    ctr = Column(Float)
    male = Column(Float)
    female = Column(Float)
    a00 = Column(Float)
    a10 = Column(Float)
    a20 = Column(Float)
    a30 = Column(Float)
    a40 = Column(Float)
    a50 = Column(Float)
    a60 = Column(Float)

    @classmethod
    def readline(cls, line):
        ls = [l.strip() for l in line.split("\t")]
        if len(ls) != 13:
            raise RuntimeError("Invalid format for %s: %s"
                % (cls.__name__, line))
        args = {attr: ls[i] for i, attr in enumerate(cls.ORDERED_ATTRS)}
        result = Clickthrough(**args)
        # convertion
        result.rank = int(result.rank)
        for attr in cls.ORDERED_ATTRS[3:]:
            setattr(result, attr, float(getattr(result, attr)))

        return result
