import pytest
import sys, os, shutil
import flask
import re
import json
from web.app import app, MAX_ASSIGNMENT
from web.schedule import Schedule
from web.evaluation import Evaluation
from web.tests.test_app import TestApp

class TestQuestion(TestApp):

    def test_question_get(self, client):
        response = client.get('/', follow_redirects=True)
        response = client.get('/api/OLQ-0001/0')
        data = json.loads(response.data.decode())
        schedule = Schedule.find(1, 'OLQ-0001', 0)
        question_ids = json.loads(schedule.question_ids)
        for qid, d in zip(question_ids, data):
            assert qid == d["question_id"]
        evaluations = Evaluation.find_votes(1, 'OLQ-0001', question_ids)
        assert all([not evaluations[qid] for qid in question_ids])

        # next
        response = client.get('/api/OLQ-0001/1')
        data = json.loads(response.data.decode())
        assert all([not d["question_id"] in question_ids for d in data])

    def test_question_post(self, client):
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
        data = json.loads(response.data.decode())
        data = {d['question_id']: d['evaluation'] for d in data}
        assert data[qid]
        assert all([not data[q] for q in data if q != qid])
