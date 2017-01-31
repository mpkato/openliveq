from flask_script import Manager
from web.app import app
import os, sys

manager = Manager(app)

@manager.command
def query_load(filepath):
    '''
    Load a set of queries from a given filepath
    '''
    from web.query import Query
    from openliveq.db import SessionContextFactory

    print("query_filepath: %s" % filepath)

    scf = SessionContextFactory()
    with scf.create() as session:
        with open(filepath) as f:
            for line in f:
                q = Query.readline(line)
                session.add(q)
        session.commit()
        print("%s queries loaded" % session.query(Query).count())

@manager.command
def unload():
    '''
    Drop all the data from the table
    '''
    from web.query import Query
    from web.schedule import Schedule
    import openliveq as olq
    from openliveq.db import SessionContextFactory
    scf = SessionContextFactory()
    engine = scf.session_factory.engine
    olq.Question.__table__.drop(engine, checkfirst=True)
    olq.Clickthrough.__table__.drop(engine, checkfirst=True)
    Query.__table__.drop(engine, checkfirst=True)
    Schedule.__table__.drop(engine, checkfirst=True)

@manager.command
def init_schedule(num):
    '''
    Initialize [num] user schedules for a given [num]
    '''
    from web.schedule import Schedule
    for user_id in range(1, int(num)+1):
        Schedule.init(user_id)

@manager.command
def destroy():
    '''
    Drop the collected data from the table
    '''
    from web.user import User
    from web.user_log import UserLog
    from web.schedule import Schedule
    from web.status import Status
    from web.evaluation import Evaluation
    from openliveq.db import SessionContextFactory
    scf = SessionContextFactory()
    engine = scf.session_factory.engine
    User.__table__.drop(engine, checkfirst=True)
    UserLog.__table__.drop(engine, checkfirst=True)
    Schedule.__table__.drop(engine, checkfirst=True)
    Status.__table__.drop(engine, checkfirst=True)
    Evaluation.__table__.drop(engine, checkfirst=True)

if __name__ == "__main__":
    manager.run()
