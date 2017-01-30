import pytest
import sys, os, shutil
import flask
from web.app import app, MAX_ASSIGNMENT
from web.status import Status
from web.user import User
from web.tests.test_app import TestApp

class TestStart(TestApp):

    def test_redirect(self, client):
        response = client.get('/')
        assert response.status_code == 302
        assert response.headers['Location'].endswith("/start")

    def test_entrance(self, client):
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
        assert "data-query=" in str(response.data)
        query_id = Status.find(1, MAX_ASSIGNMENT)
        assert query_id == "OLQ-0001"

        another_client = app.test_client()
        response = another_client.get('/', follow_redirects=True)
        assert response.status_code == 200
        assert "data-query=" in str(response.data)
        query_id = Status.find(2, MAX_ASSIGNMENT)
        assert query_id == "OLQ-0003"

    def test_too_many_entrance(self):
        for i in range(MAX_ASSIGNMENT * 3):
            response = app.test_client().get('/', follow_redirects=True)
            assert response.status_code == 200
            assert "data-query=" in str(response.data)

        response = app.test_client().get('/', follow_redirects=True)
        assert response.status_code == 200
        assert not "data-query=" in str(response.data)
        assert 'class="over"' in str(response.data)

    def test_reentrance(self, client):
        for i in range(3):
            response = client.get('/', follow_redirects=True)
            assert response.status_code == 200
            assert 'data-query="OLQ-0001"' in str(response.data)
        assert User.find(2) is None
