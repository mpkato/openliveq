import pytest
import sys, os, shutil
import flask
import re
import time
from web.app import app, MAX_ASSIGNMENT
from web.user_log import UserLog
from web.tests.test_app import TestApp

class TestUserLog(TestApp):
    CODE = re.compile(r'([0-9]{4})-([0-9]{4})-([0-9]{4})-([0-9]{4})')

    def test_find_all(self, client):
        response = client.get('/', follow_redirects=True)
        response = client.get('/api/OLQ-0001/0')
        logs = UserLog.find_all(1)
        assert logs[0].action == '/api/OLQ-0001/0'
        assert logs[0].query_id == 'OLQ-0001'
        assert logs[1].action == '/OLQ-0001/0'
        assert logs[1].query_id == 'OLQ-0001'
        assert logs[2].action == '/start'
        assert logs[2].query_id is None
        response = client.get('/next/OLQ-0001/0', follow_redirects=True)
        logs = UserLog.find_all(1)
        assert logs[0].action == '/OLQ-0001/1'
        assert logs[1].action == '/next/OLQ-0001/0'
        response = client.get('/next/OLQ-0001/1', follow_redirects=True)
        logs = UserLog.find_all(1)
        assert logs[0].action == '/next/OLQ-0001/1'

    def test_find_latest(self, client):
        log = UserLog.find_latest(1)
        assert log is None
        response = client.get('/', follow_redirects=True)
        response = client.get('/api/OLQ-0001/0')
        log = UserLog.find_latest(1)
        assert log.action == '/api/OLQ-0001/0'
        response = client.get('/next/OLQ-0001/0', follow_redirects=True)
        log = UserLog.find_latest(1)
        assert log.action == '/OLQ-0001/1'
        response = client.get('/next/OLQ-0001/1', follow_redirects=True)
        log = UserLog.find_latest(1)
        assert log.action == '/next/OLQ-0001/1'

    def test_find_inactive_users(self, client):
        response = client.get('/', follow_redirects=True)
        time.sleep(0.1)
        response = app.test_client().get('/', follow_redirects=True)
        user_ids = UserLog.find_inactive_users(0.1)
        assert set(user_ids) == set([1])
        time.sleep(0.1)
        user_ids = UserLog.find_inactive_users(0.1)
        assert set(user_ids) == set([1, 2])

    def test_compute_ellapsed_time(self, client):
        response = client.get('/', follow_redirects=True)
        time.sleep(0.1)
        response = client.get('/', follow_redirects=True)
        ellapsed_time = UserLog.compute_ellapsed_time(1, 'OLQ-0001')
        assert ellapsed_time > 0
        ellapsed_time = UserLog.compute_ellapsed_time(1, 'OLQ-0003')
        assert ellapsed_time == 0
        response = app.test_client().get('/', follow_redirects=True)
        ellapsed_time = UserLog.compute_ellapsed_time(2, 'OLQ-0003')
        assert ellapsed_time == 0

    def test_generate_code(self, client):
        url = '/'
        for i in range(2):
            response = client.get(url, follow_redirects=True)
            url = self.A_HREF.search(response.data.decode()).group(1)
        response = client.get(url, follow_redirects=True)
        assert 'class="code"' in response.data.decode()
        match = self.CODE.search(response.data.decode())
        assert match is not None
        assert int(match.group(1)) == 0
        assert int(match.group(3)) == 1
        assert int(match.group(4)) == 1

        client = app.test_client()
        url = '/'
        for i in range(2):
            response = client.get(url, follow_redirects=True)
            url = self.A_HREF.search(response.data.decode()).group(1)
            time.sleep(1)
        response = client.get(url, follow_redirects=True)
        match = self.CODE.search(response.data.decode())
        assert match is not None
        assert int(match.group(1)) == 1
        assert int(match.group(3)) == 2
        assert int(match.group(4)) == 3
