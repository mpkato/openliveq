from sqlalchemy import Column, Integer, String, Boolean, Index, ForeignKey
from sqlalchemy import func, case
from openliveq.db import Base, SessionContextFactory
from web.query import Query
from web.user_log import UserLog
import numpy as np

class Status(Base):
    __tablename__ = 'statuses'
    __table_args__ = (
        Index('statuses_user_id_index', "user_id"),
        Index('statuses_user_id_query_id_index', "user_id", "query_id"),
        Index('statuses_user_id_is_done_index', "user_id", "is_done"),
        )
    user_id = Column(Integer, primary_key=True)
    query_id = Column(String(8), primary_key=True)
    is_done = Column(Boolean)

    @classmethod
    def init(cls, user_id, query_id):
        '''
        Insert a record of user_id and query_id with is_done = False
        '''
        scf = SessionContextFactory()
        with scf.create() as session:
            status = session.query(Status)\
                .filter(Status.user_id == user_id,
                Status.query_id == query_id).first()
            if status is None:
                status = Status(user_id=user_id,
                    query_id=query_id, is_done=False)
                session.add(status)
                session.commit()

    @classmethod
    def finalize(cls, user_id, query_id):
        '''
        Set True to is_done for user_id and query_id
        '''
        scf = SessionContextFactory()
        with scf.create() as session:
            status = session.query(Status)\
                .filter(Status.user_id == user_id,
                Status.query_id == query_id).first()
            if status is not None:
                status.is_done = True
                session.commit()

        return (status is not None)

    @classmethod
    def is_valid(cls, user_id, query_id):
        '''
        Find a record of user_id and query_id,
        and return True if it exists and is_done = False;
        otherwise False
        '''
        scf = SessionContextFactory()
        with scf.create() as session:
            status = session.query(Status)\
                .filter(Status.user_id == user_id,
                Status.query_id == query_id).first()
        if status is None or status.is_done:
            return False
        else:
            return True

    @classmethod
    def find(cls, user_id, max_num):
        '''
        Find the next query that still needs assignment (# trials < max_num)
        and has not been presented to the user
        '''
        scf = SessionContextFactory()
        with scf.create() as session:
            # find an incomplete query_id
            status = session.query(Status)\
                .filter(Status.user_id == user_id,
                Status.is_done == False).first()
            if status is not None:
                return status.query_id

            # find a query_id that needs assignments
            queries = session.query(Query).all()
            queries = [q.query_id for q in queries]
            np.random.seed(user_id)
            np.random.shuffle(queries)
            counts = session.query(Status.query_id,
                func.count(Status.user_id))\
                .group_by(Status.query_id).all()
            counts = {c[0]: c[1] for c in counts}
            done = session.query(Status)\
                .filter(Status.user_id == user_id,
                Status.is_done == True).all()
            done = {s.query_id for s in done}
        # the number of trials should be less than max_num
        queries = [q for q in queries if counts.get(q, 0) < max_num]
        # should not be tackled
        queries = [q for q in queries if not q in done]
        if len(queries) > 0:
            # give priority to queries with less count
            queries = sorted(queries, key=lambda q: counts.get(q, 0))
            return queries[0]
        else:
            return None

    @classmethod
    def find_all_by_user_id(cls, user_id):
        scf = SessionContextFactory()
        with scf.create() as session:
            statuses = session.query(Status)\
                .filter(Status.user_id == user_id).all()
        return statuses

    @classmethod
    def cleanup(cls, max_time_interval):
        user_ids = UserLog.find_inactive_users(max_time_interval)
        if len(user_ids) > 0:
            scf = SessionContextFactory()
            with scf.create() as session:
                session.query(Status)\
                    .filter(Status.is_done == False,
                    Status.user_id.in_(user_ids))\
                    .delete(synchronize_session=False)
                session.commit()

    @classmethod
    def query_summary(cls):
        scf = SessionContextFactory()
        with scf.create() as session:
            statuses = session.query(
                Status.query_id,
                func.count(),
                func.sum(case([
                    (Status.is_done == True, 1),
                    (Status.is_done == False, 0)
                ]))
                )\
                .group_by(Status.query_id)\
                .all()
        return statuses
