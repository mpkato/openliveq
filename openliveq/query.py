from sqlalchemy import Column, String
from .db import Base

class Query(Base):
    __tablename__ = 'queries'

    ORDERED_ATTRS = ["query_id", "body"]

    query_id = Column(String(8), primary_key=True)
    body = Column(String(255))

    @classmethod
    def readline(cls, line):
        ls = [l.strip() for l in line.split("\t")]
        if len(ls) != 2:
            return None
        args = {attr: ls[i] for i, attr in enumerate(cls.ORDERED_ATTRS)}
        result = Query(**args)
        return result
