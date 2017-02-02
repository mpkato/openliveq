from sqlalchemy import Column, Integer, String, Boolean, Text, Index
from openliveq.db import Base, SessionContextFactory
from openliveq.question import Question
from web.query import Query
import numpy as np
import json

class Schedule(Base):
    NUM_QUESTION = 10 # the number of questions in a chunk

    __tablename__ = 'schedules'
    __table_args__ = (
        Index('schedules_user_id_query_id_index', "user_id", "query_id"),
        Index('schedules_user_id_query_id_order_index',
            "user_id", "query_id", "order"),
        Index('schedules_user_id_query_id_is_done_index',
            "user_id", "query_id", "is_done"),
        Index('schedules_user_id_query_id_is_done_order_index',
            "user_id", "query_id", "is_done", "order"),
        )
    user_id = Column(Integer, primary_key=True)
    query_id = Column(String(8), primary_key=True)
    order = Column(Integer, primary_key=True)
    question_ids = Column(Text)
    is_done = Column(Boolean)

    @classmethod
    def init(cls, user_id, query_id):
        '''
        Prepare chunks of question_ids for user_id.
        The order of question_ids is randomized with user_id as a seed
        '''
        scf = SessionContextFactory()
        with scf.create() as session:
            s = session.query(Schedule)\
                .filter(Schedule.user_id == user_id,
                Schedule.query_id == query_id).first()
            if s is not None:
                return
            question_ids = session.query(Question.question_id)\
                .filter(Question.query_id == query_id).all()
            question_ids = [qid[0] for qid in question_ids]
            np.random.seed(user_id)
            np.random.shuffle(question_ids)
            iternum = (len(question_ids) - 1) // cls.NUM_QUESTION + 1
            for i in range(iternum):
                start = i*cls.NUM_QUESTION
                end = (i+1)*cls.NUM_QUESTION
                qids = question_ids[start:end]
                s = Schedule(user_id=user_id, query_id=query_id,
                    order=i, question_ids=json.dumps(qids),
                    is_done=False)
                session.add(s)
            session.commit()

    @classmethod
    def find(cls, user_id, query_id, order):
        scf = SessionContextFactory()
        with scf.create() as session:
            schedule = session.query(Schedule)\
                .filter(Schedule.user_id == user_id,
                Schedule.query_id == query_id,
                Schedule.order == order).first()
        return schedule

    @classmethod
    def finalize(cls, user_id, query_id, order):
        '''
        Set True to is_done of the schedule
        '''
        scf = SessionContextFactory()
        with scf.create() as session:
            schedule = session.query(Schedule)\
                .filter(Schedule.user_id == user_id,
                Schedule.query_id == query_id,
                Schedule.order == order).first()
            if schedule is not None:
                schedule.is_done = True
                session.commit()

    @classmethod
    def find_next(cls, user_id, query_id):
        '''
        Find the next schedule whose is_done = False and order is minimum
        '''
        scf = SessionContextFactory()
        with scf.create() as session:
            schedule = session.query(Schedule)\
                .filter(Schedule.user_id == user_id,
                Schedule.query_id == query_id,
                Schedule.is_done == False)\
                .order_by(Schedule.order).first()
        return schedule


    @classmethod
    def find_all(cls, user_id, query_id):
        scf = SessionContextFactory()
        with scf.create() as session:
            schedules = session.query(Schedule)\
                .filter(Schedule.user_id == user_id,
                Schedule.query_id == query_id)\
                .order_by(Schedule.order).all()
        return schedules
