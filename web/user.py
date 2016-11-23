from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from openliveq.db import Base, SessionContextFactory

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement': True}
    user_id = Column(Integer, primary_key=True)

    @classmethod
    def create(cls):
        scf = SessionContextFactory()
        with scf.create() as session:
            user = User()
            session.add(user)
            session.commit()
        return user

    @classmethod
    def find(cls, user_id):
        scf = SessionContextFactory()
        with scf.create() as session:
            user = session.query(User).\
                filter(User.user_id == user_id).first()
        return user
