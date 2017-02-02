import pytest
import sys, os, shutil
import flask
import re
import json
from web.app import app, MAX_ASSIGNMENT
from web.schedule import Schedule
from web.evaluation import Evaluation
from web.tests.test_app import TestApp

class TestEvaluation(TestApp):

    def test_summary(self, client):
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

        res = Evaluation.summary()
        assert res[0] == (1, 'OLQ-0001', 10, 1)

        qids = [d['question_id'] for d in data[:2]]
        submitdata = json.dumps({"evaluations": [{
            "question_id": d['question_id'],
            "evaluation": d['question_id'] in qids
            }
            for d in data]})
        response = client.post('/api/OLQ-0001/0', data=submitdata,
            headers={'Content-Type': 'application/json'})

        res = Evaluation.summary()
        assert res[0] == (1, 'OLQ-0001', 10, 2)

        response = client.get('/api/OLQ-0001/1')
        data = json.loads(response.data.decode())
        qid = data[0]['question_id']
        submitdata = json.dumps({"evaluations": [{
            "question_id": d['question_id'],
            "evaluation": qid == d['question_id']
            }
            for d in data]})
        response = client.post('/api/OLQ-0001/1', data=submitdata,
            headers={'Content-Type': 'application/json'})

        res = Evaluation.summary()
        assert res[0] == (1, 'OLQ-0001', 20, 3)
