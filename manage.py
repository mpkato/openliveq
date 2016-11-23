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
    scf = SessionContextFactory()
    engine = scf.session_factory.engine
    olq.Question.__table__.drop(engine, checkfirst=True)
    olq.Clickthrough.__table__.drop(engine, checkfirst=True)
    Query.__table__.drop(engine, checkfirst=True)
    print("DONE!")

if __name__ == "__main__":
    manager.run()
