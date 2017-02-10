import re
import datetime
import numpy as np
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, desc
from sqlalchemy import func
from openliveq.db import Base, SessionContextFactory
from web.schedule import Schedule

class UserLog(Base):
    __tablename__ = 'user_logs'
    __table_args__ = (
        Index('user_logs_user_id_index', "user_id"),
        Index('user_logs_user_id_query_id_index', "user_id", "query_id"),
        Index('user_logs_user_id_created_at_index', "user_id", "created_at"),
        {'sqlite_autoincrement': True}
    )
    user_log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    query_id = Column(String(8))
    action = Column(String(20))
    created_at = Column(DateTime)

    QUERY_ID = re.compile(r'OLQ-[0-4]{4}')
    CODE = '%04d-%04d-%04d'

    @classmethod
    def create(cls, user_id, action):
        m = cls.QUERY_ID.search(action)
        query_id = None if m is None else m.group(0)
        scf = SessionContextFactory()
        with scf.create() as session:
            now = datetime.datetime.now()
            log = UserLog(user_id=user_id, query_id=query_id,
                action=action, created_at=now)
            session.add(log)
            session.commit()
        return log

    @classmethod
    def find_all(cls, user_id):
        scf = SessionContextFactory()
        with scf.create() as session:
            logs = session.query(UserLog).\
                filter(UserLog.user_id == user_id)\
                .order_by(desc(UserLog.created_at)).all()
        return logs

    @classmethod
    def find_latest(cls, user_id):
        scf = SessionContextFactory()
        with scf.create() as session:
            log = session.query(UserLog).\
                filter(UserLog.user_id == user_id)\
                .order_by(desc(UserLog.created_at)).first()
        return log

    @classmethod
    def find_inactive_users(cls, max_time_interval):
        delta = datetime.timedelta(seconds=max_time_interval)
        threshold = datetime.datetime.now() - delta
        scf = SessionContextFactory()
        with scf.create() as session:
            logs = session.query(UserLog)\
                .group_by(UserLog.user_id)\
                .having(func.max(UserLog.created_at) < threshold)\
                .all()
        user_ids = [l.user_id for l in logs]
        return user_ids

    @classmethod
    def compute_ellapsed_time(cls, user_id, query_id):
        scf = SessionContextFactory()
        with scf.create() as session:
            max_time = session.query(func.max(UserLog.created_at))\
                .filter(UserLog.user_id == user_id,
                UserLog.query_id == query_id).first()[0]
            min_time = session.query(func.min(UserLog.created_at))\
                .filter(UserLog.user_id == user_id,
                UserLog.query_id == query_id).first()[0]
        if max_time is not None and min_time is not None:
            result = (max_time - min_time).total_seconds()
        else:
            result = 0
        return result

    @classmethod
    def generate_code(cls, user_id, query_id):
        ellapsed_time = cls.compute_ellapsed_time(user_id, query_id)
        schedules = Schedule.find_all(user_id, query_id)
        num_schedules = len(schedules)
        avg_ellapsed_time = 0.0 if num_schedules == 0\
            else int(ellapsed_time / num_schedules)
        qid = int(query_id[4:])
        return cls.CODE % (avg_ellapsed_time, user_id, qid)
