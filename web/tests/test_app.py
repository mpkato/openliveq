import pytest
import os, shutil
import re
from web.app import app

class TestApp(object):
    A_HREF = re.compile(r'<a [^>]*?href="(.*?)"[^>]*?>')

    @pytest.fixture
    def client(self):
        return app.test_client()

    @pytest.fixture(autouse=True, scope='function')
    def scope_function(self, request):
        rootdir = os.path.join(os.path.dirname(__file__), "..", "..")
        srcpath = os.path.join(rootdir, "web", "tests", "fixtures",
            "db.sqlite3")
        dstpath = os.path.join(rootdir, "openliveq", "db.sqlite3")
        shutil.copy(srcpath, dstpath)
        def fin_scope_function():
            shutil.copy(srcpath, dstpath)
        request.addfinalizer(fin_scope_function)
