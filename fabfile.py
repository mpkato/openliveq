from fabric.api import env, cd, run, put
from fabric.contrib.files import exists
from settings import HOST, REMOTE_HOME, REMOTE_PYTHON_HOME, KEY_PATH
import sys

env.hosts = [HOST]
env.key_filename = KEY_PATH

def deploy():
    with cd(REMOTE_HOME):
        if exists("current"):
            if exists("current/openliveq/db.sqlite3"):
                run("mv current/openliveq/db.sqlite3 ./")
            run("rm -rf current")
            run("mkdir current")
        with cd("repo"):
            run("git pull origin web")
            run("git archive web | tar -x -f - -C %s/current" % REMOTE_HOME)
        with cd("current"):
            run("%s/bin/python setup.py install --force" % REMOTE_PYTHON_HOME)
            run("%s/bin/pip install -r web_requirements.txt" % REMOTE_PYTHON_HOME)
        if exists("db.sqlite3"):
            run("mv db.sqlite3 current/openliveq/")
        run('touch .uwsgi_touch')

def upload(filepath):
    with cd(REMOTE_HOME):
        put(filepath, "resources/")

def load():
    with cd(REMOTE_HOME):
        if not exists("resources/OpenLiveQ-question-data.tsv")\
            or not exists("resources/OpenLiveQ-clickthrough.tsv"):
            print("File not found")
            sys.exit(1)

        with cd("current"):
            run("""%s/bin/openliveq load \
            ../resources/OpenLiveQ-question-data.tsv \
            ../resources/OpenLiveQ-clickthrough.tsv""" % REMOTE_PYTHON_HOME)
