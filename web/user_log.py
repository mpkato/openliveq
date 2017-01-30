import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, desc
from openliveq.db import Base, SessionContextFactory

class UserLog(Base):
    __tablename__ = 'user_logs'
    __table_args__ = (
        Index('user_logs_user_id_index', "user_id"),
        Index('user_logs_user_id_created_at_index', "user_id", "created_at"),
        {'sqlite_autoincrement': True}
    )
    user_log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String(20))
    created_at = Column(DateTime)

    @classmethod
    def create(cls, user_id, action):
        scf = SessionContextFactory()
        with scf.create() as session:
            now = datetime.datetime.now()
            log = UserLog(user_id=user_id, action=action, created_at=now)
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
