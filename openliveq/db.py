import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
Base = declarative_base()
DBPATH = '%s/db.sqlite3' % os.path.abspath(os.path.dirname(__file__))
BULK_RATE = 1000

class SessionFactory(object):

    def __init__(self, echo=False):
        self.engine = create_engine('sqlite:///%s' % DBPATH, echo=echo)
        Base.metadata.create_all(self.engine)

    def create(self):
        Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        return Session()

class SessionContext(object):

    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.flush()
        self.session.commit()
        self.session.close()

class SessionContextFactory(object):

    def __init__(self, echo=False):
        self.session_factory = SessionFactory(echo)

    def create(self):
        return SessionContext(self.session_factory.create())
