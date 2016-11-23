from flask_script import Manager
from web.app import app
import os, sys

manager = Manager(app)

@manager.command
def query_load():
    from web.query import Query
    filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)),
        "..", "resources", "OpenLiveQ-queries-test.tsv")
    scf = SessionContextFactory()
    with scf.create() as session:
        with open(filepath) as f:
            for line in f:
                q = Query.readline(line)
                session.add(q)
        session.commit()

@manager.command
def unload():
    from web.query import Query
    import openliveq as olq
    from openliveq.db import SessionContextFactory
    scf = SessionContextFactory()
    engine = scf.session_factory.engine
    olq.Question.__table__.drop(engine, checkfirst=True)
    olq.Clickthrough.__table__.drop(engine, checkfirst=True)
    Query.__table__.drop(engine, checkfirst=True)

if __name__ == "__main__":
    manager.run()
