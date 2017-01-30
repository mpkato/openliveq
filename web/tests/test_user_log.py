import pytest
import sys, os, shutil
import flask
import re
from web.app import app, MAX_ASSIGNMENT
from web.user_log import UserLog
from web.tests.test_app import TestApp

class TestUserLog(TestApp):

    def test_find_all(self, client):
        response = client.get('/', follow_redirects=True)
        response = client.get('/api/OLQ-0001/0')
        logs = UserLog.find_all(1)
        assert logs[0].action == '/api/OLQ-0001/0'
        assert logs[1].action == '/OLQ-0001/0'
        assert logs[2].action == '/start'
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
