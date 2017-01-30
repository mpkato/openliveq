from sqlalchemy import Column, Integer, String, Boolean, Index, ForeignKey
from openliveq.db import Base, SessionContextFactory

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

    @classmethod
    def find_votes(cls, user_id, query_id, question_ids):
        '''
        Find votes for question_ids,
        and create evaluations if votes are not found
        '''
        scf = SessionContextFactory()
        with scf.create() as session:
            evaluations = session.query(Evaluation)\
                .filter(Evaluation.user_id == user_id,
                Evaluation.query_id == query_id,
                Evaluation.question_id.in_(question_ids)).all()
            evaluations = {e.question_id: e.vote for e in evaluations}
            for qid in question_ids:
                if not qid in evaluations:
                    e = Evaluation(user_id=user_id,
                        query_id=query_id, 
                        question_id=qid,
                        vote=False)
                    session.add(e)
                    evaluations[qid] = e.vote
            session.commit()
        return evaluations