import pytest
import sys, os, shutil
import flask
import re
from web.app import app, MAX_ASSIGNMENT
from web.status import Status
from web.user import User
from web.tests.test_app import TestApp

class TestNext(TestApp):
    A_HREF = re.compile(r'<a [^>]*?href="(.*?)"[^>]*?>')

    def test_next(self, client):
        url = '/'
        for i in range(2):
            response = client.get(url, follow_redirects=True)
            url = self.A_HREF.search(response.data.decode()).group(1)
            status = Status.find_all_by_user_id(1)[0]
            assert not status.is_done
        response = client.get(url, follow_redirects=True)
        assert "Lancers" in response.data.decode()
        status = Status.find_all_by_user_id(1)[0]
        assert status.is_done

    def test_start_after_next(self, client):
        url = '/'
        for i in range(2):
            response = client.get(url, follow_redirects=True)
            url = self.A_HREF.search(response.data.decode()).group(1)
        url = '/'
        response = client.get(url, follow_redirects=True)
        url = self.A_HREF.search(response.data.decode()).group(1)
        assert url == "/next/OLQ-0001/1"

    def test_finish_and_next(self, client):
        url = '/'
        for i in range(2):
            response = client.get(url, follow_redirects=True)
            assert "OLQ-0001" in response.data.decode()
            url = self.A_HREF.search(response.data.decode()).group(1)
        # finish
        response = client.get(url, follow_redirects=True)
        status = Status.find_all_by_user_id(1)[0]
        assert status.is_done

        # next query
        url = '/'
        response = client.get(url, follow_redirects=True)
        assert "OLQ-0003" in response.data.decode()
        statuses = Status.find_all_by_user_id(1)
        assert len(statuses) == 2
        assert any([s.is_done for s in statuses])
        assert not all([s.is_done for s in statuses])

    def test_invalid_serp(self, client):
        response = client.get('/', follow_redirects=True)
        assert "OLQ-0001" in response.data.decode()
        response = client.get('/OLQ-0002/0', follow_redirects=True)
        assert "OLQ-0001" in response.data.decode()

    def test_invalid_order(self, client):
        response = client.get('/', follow_redirects=True)
        assert "OLQ-0001" in response.data.decode()
        response = client.get('/next/OLQ-0001/2', follow_redirects=True)
        url = self.A_HREF.search(response.data.decode()).group(1)
        assert url == "/next/OLQ-0001/0"

    def test_finish_and_invalid_serp(self, client):
        url = '/'
        for i in range(2):
            response = client.get(url, follow_redirects=True)
            assert "OLQ-0001" in response.data.decode()
            url = self.A_HREF.search(response.data.decode()).group(1)
        # finish
        response = client.get(url, follow_redirects=True)

        response = client.get('/OLQ-0001/0', follow_redirects=True)
        url = self.A_HREF.search(response.data.decode()).group(1)
        assert url == "/next/OLQ-0003/0"

    def test_no_cookie(self, client):
        response = client.get('/OLQ-0001/0', follow_redirects=True)
        assert response.status_code == 200
        assert "OLQ-0001" in response.data.decode()
