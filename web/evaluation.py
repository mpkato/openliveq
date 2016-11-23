from sqlalchemy import Column, Integer, String, Boolean, Index, ForeignKey
from openliveq.db import Base

class Evaluation(Base):
    __tablename__ = 'evaluations'
    __table_args__ = (
        Index('questions_user_id_index', "user_id"),
        Index('questions_user_id_query_id_index', "user_id", "query_id"),
        )
    user_id = Column(Integer, primary_key=True)
    query_id = Column(String(8), primary_key=True)
    question_id = Column(String(12), primary_key=True)
    vote = Column(Boolean)
