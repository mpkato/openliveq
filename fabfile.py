from fabric.api import env, cd, run
from fabric.contrib.files import exists
from settings import HOST, REMOTE_HOME, REMOTE_PYTHON_HOME, KEY_PATH

env.hosts = [HOST]
env.key_filename = KEY_PATH

def deploy():
    with cd(REMOTE_HOME):
        if exists("current"):
            run("rm -rf current")
            run("mkdir current")
        with cd("repo"):
            run("git pull origin web")
            run("git archive web | tar -x -f - -C %s/current" % REMOTE_HOME)
        with cd("current"):
            run("%s/bin/python setup.py install --force" % REMOTE_PYTHON_HOME)
            run("%s/bin/pip install -r web_requirements.txt" % REMOTE_PYTHON_HOME)
        run('touch .uwsgi_touch')
