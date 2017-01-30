import pytest
import sys, os, shutil
import flask
import re
import time
from web.app import app, MAX_ASSIGNMENT
from web.user_log import UserLog
from web.status import Status
from web.tests.test_app import TestApp

class TestStatus(TestApp):

    def test_cleanup(self):
        client = None
        for i in range(MAX_ASSIGNMENT * 3):
            client = app.test_client()
            response = client.get('/', follow_redirects=True)
            assert response.status_code == 200
            assert "data-query=" in response.data.decode()

        response = app.test_client().get('/', follow_redirects=True)
        assert response.status_code == 200
        assert not "data-query=" in response.data.decode()
        assert 'class="over"' in response.data.decode()

        time.sleep(0.1)
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
        assert "data-query=" in response.data.decode()

        Status.cleanup(0.1)
        for i in range(MAX_ASSIGNMENT * 3 - 1):
            response = app.test_client().get('/', follow_redirects=True)
            assert response.status_code == 200
            assert "data-query=" in response.data.decode()

        response = app.test_client().get('/', follow_redirects=True)
        assert response.status_code == 200
        assert not "data-query=" in response.data.decode()
        assert 'class="over"' in response.data.decode()
