from flask_script import Manager
from web.app import app

manager = Manager(app)

@manager.command
def query_load():
    print("hello")

@manager.command
def unload():
    from web.query import Query
    import openliveq as olq
    from openliveq.db import SessionContextFactory
    if exists(DBPATH):
        scf = SessionContextFactory()
        engine = scf.session_factory.engine
        olq.Question.__table__.drop(engine)
        olq.Clickthrough.__table__.drop(engine)
        Query.__table__.drop(engine)

if __name__ == "__main__":
    manager.run()
