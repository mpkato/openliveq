import pytest
import sys, os, shutil
import flask
import re
import json
from web.app import app, MAX_ASSIGNMENT
from web.schedule import Schedule
from web.evaluation import Evaluation
from web.tests.test_app import TestApp

class TestAdmin(TestApp):

    def test_question_get(self, client):
        response = client.get('/admin', follow_redirects=True)
        assert not 'OLQ-0001' in response.data.decode()

        response = client.get('/', follow_redirects=True)
        response = client.get('/api/OLQ-0001/0')
        data = json.loads(response.data.decode())
        qid = data[0]['question_id']
        submitdata = json.dumps({"evaluations": [{
            "question_id": d['question_id'],
            "evaluation": qid == d['question_id']
            }
            for d in data]})
        response = client.post('/api/OLQ-0001/0', data=submitdata,
            headers={'Content-Type': 'application/json'})

        response = client.get('/admin', follow_redirects=True)
        assert 'OLQ-0001' in response.data.decode()
