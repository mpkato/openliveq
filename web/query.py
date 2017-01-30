from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from openliveq.db import Base, SessionContextFactory

class Query(Base):
    __tablename__ = 'queries'
    query_id = Column(String(8), primary_key=True)
    body = Column(String(255))

    @classmethod
    def readline(cls, line):
        ls = [l.strip() for l in line.split("\t")]
        if len(ls) != 2:
            raise RuntimeError("Invalid format for %s: %s"
                % (cls.__name__, line))
        result = Query(query_id=ls[0], body=ls[1])
        return result

    @classmethod
    def find(cls, query_id):
        scf = SessionContextFactory()
        with scf.create() as session:
            query = session.query(Query)\
                .filter(Query.query_id == query_id).first()
        return query