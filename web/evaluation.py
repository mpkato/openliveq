from sqlalchemy import Column, Integer, String, Boolean, Index, ForeignKey
from sqlalchemy import func, case
import json
from openliveq.db import Base, SessionContextFactory
from web.schedule import Schedule
import openliveq as olq

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

    @classmethod
    def update(cls, query_id, user_id, newevals):
        '''
        Update the evaluations based on the posted data
        '''
        newevals = {e["question_id"]: e["evaluation"] for e in newevals}
        scf = SessionContextFactory()
        with scf.create() as session:
            evaluations = session.query(Evaluation)\
                .filter(Evaluation.query_id == query_id,
                Evaluation.user_id == user_id,
                Evaluation.question_id.in_(list(newevals.keys()))).all()
            evaluations = {e.question_id: e for e in evaluations}
            for question_id in newevals:
                evaluations[question_id].vote = newevals[question_id]
            session.commit()

    @classmethod
    def find_questions(cls, user_id, query_id, order):
        scf = SessionContextFactory()
        with scf.create() as session:
            schedule = Schedule.find(user_id, query_id, order)
            question_ids = json.loads(schedule.question_ids)
            questions = session.query(olq.Question)\
                .filter(olq.Question.query_id == query_id,
                olq.Question.question_id.in_(question_ids)).all()
        evaluations = cls.find_votes(user_id, query_id, question_ids)
        questions = cls._process_questions(questions, evaluations)
        questions = cls._order_questions(question_ids, questions)
        return questions

    @classmethod
    def _process_questions(cls, questions, evaluations):
        '''
        Convert questions and evaluations to dict
        '''
        for q in questions:
            q.updated_at = q.updated_at.strftime("%Y/%m/%d %H:%M:%S")
        questions = [{a: getattr(q, a) for a in q.ORDERED_ATTRS}
            for q in questions]
        for q in questions:
            q["evaluation"] = evaluations[q["question_id"]]
        return questions

    @classmethod
    def _order_questions(cls, question_ids, questions):
        '''
        Order questions in the order of question_ids
        '''
        questions = {q["question_id"]: q for q in questions}
        return [questions[qid] for qid in question_ids]

    @classmethod
    def summary(cls):
        scf = SessionContextFactory()
        with scf.create() as session:
            evaluations = session.query(
                Evaluation.user_id, Evaluation.query_id,
                func.count(), func.sum(case([
                    (Evaluation.vote == True, 1),
                    (Evaluation.vote == False, 0)
                ]))
                )\
                .group_by(Evaluation.user_id, Evaluation.query_id)\
                .all()
        return evaluations
