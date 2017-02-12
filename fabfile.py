from fabric.api import env, cd, run, put, local
from fabric.contrib.files import exists
from settings import (HOST, REMOTE_HOME, REMOTE_PYTHON_HOME, KEY_PATH,
    NUM_SCHEDULES)
import sys

DBPATH = "%s/lib/python3.5/site-packages/" % REMOTE_PYTHON_HOME\
    + "openliveq-0.0.1-py3.5.egg/openliveq/db.sqlite3"

env.hosts = [HOST]
env.key_filename = KEY_PATH

def deploy():
    local("git push origin web")
    with cd(REMOTE_HOME):
        run("mv %s ./" % DBPATH)
        if exists("current"):
            run("rm -rf current")
            run("mkdir current")
        with cd("repo"):
            run("git pull origin web")
            run("git archive web | tar -x -f - -C %s/current" % REMOTE_HOME)
        with cd("current"):
            run("%s/bin/python setup.py install --force" % REMOTE_PYTHON_HOME)
            run("%s/bin/pip install -r web_requirements.txt" % REMOTE_PYTHON_HOME)
            run("rm -rf openliveq*") # avoid conflicts
        run("mv db.sqlite3 %s" % DBPATH)
        run('touch .uwsgi_touch')

def upload(filepath):
    with cd(REMOTE_HOME):
        put(filepath, "resources/")

def load():
    with cd(REMOTE_HOME):
        if not exists("resources/OpenLiveQ-question-data.tsv")\
            or not exists("resources/OpenLiveQ-clickthrough.tsv"):
            print("File not found: OpenLiveQ-question-data.tsv and "\
                + "OpenLiveQ-clickthrough.tsv")
            sys.exit(1)
        with cd("current"):
            run("""%s/bin/openliveq load \
                ../resources/OpenLiveQ-question-data.tsv \
                ../resources/OpenLiveQ-clickthrough.tsv""" % REMOTE_PYTHON_HOME)

        if not exists("resources/OpenLiveQ-queries-test.tsv"):
            print("File not found: OpenLiveQ-queries-test.tsv")
            sys.exit(1)

        with cd("current"):
            run("""%s/bin/python manage.py query_load \
                ../resources/OpenLiveQ-queries-test.tsv""" % REMOTE_PYTHON_HOME)

def unload():
    with cd(REMOTE_HOME):
        with cd("current"):
            run("%s/bin/python manage.py unload" % REMOTE_PYTHON_HOME)

def reload():
    unload()
    load()

def destroy():
    with cd(REMOTE_HOME):
        with cd("current"):
            run("""%s/bin/python manage.py destroy""" % REMOTE_PYTHON_HOME)

def init_schedule():
    with cd(REMOTE_HOME):
        with cd("current"):
            run("%s/bin/python manage.py init_schedule %s" % (
                REMOTE_PYTHON_HOME, NUM_SCHEDULES))
