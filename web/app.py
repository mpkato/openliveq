from flask import (Flask, render_template, redirect, url_for, 
    jsonify, request, g)
import json
import openliveq as olq
from web.query import Query
from web.user import User
from web.schedule import Schedule
from web.status import Status
from web.evaluation import Evaluation
from openliveq.db import SessionContextFactory

app = Flask(__name__)

MAX_ASSIGNMENT = 15

@app.route('/')
def index():
    return redirect(url_for('start'))

@app.route('/start')
def start():
    query_id = Status.find(g.user.user_id, MAX_ASSIGNMENT)
    if query_id is not None:
        Status.init(g.user.user_id, query_id)
        schedule = Schedule.find_next(g.user.user_id, query_id)
        if schedule is not None:
            return redirect(url_for('serp',
                query_id=query_id, order=schedule.order))
        else:
            return redirect(url_for('next', query_id=query_id, order=0))
    else:
        return redirect(url_for('over'))

@app.route('/<query_id>/<order>')
def serp(query_id, order):
    '''
    Show the <order>-th list of questions for <query_id>
    '''
    if not Status.is_valid(g.user.user_id, query_id):
        return redirect(url_for('index'))
    else:
        query = Query.find(query_id)
        return render_template('serp.html', query=query, order=order)

@app.route('/api/<query_id>/<order>', methods=['POST', 'GET'])
def questions(query_id, order):
    '''
    GET: Return the <order>-th list of questions for <query_id>
    POST: Update the evaluations based on the posted data and do the same as GET
    '''
    if request.method == 'POST':
        _questions_post(query_id)

    scf = SessionContextFactory()
    with scf.create() as session:
        schedule = Schedule.find(g.user.user_id, query_id, order)
        question_ids = json.loads(schedule.question_ids)
        questions = session.query(olq.Question)\
            .filter(olq.Question.query_id == query_id,
            olq.Question.question_id.in_(question_ids)).all()
    evaluations = Evaluation.find_votes(
        g.user.user_id, query_id, question_ids)
    questions = _process_questions(questions, evaluations)
    questions = _order_questions(question_ids, questions)
    return jsonify(questions)

@app.route('/next/<query_id>/<order>')
def next(query_id, order):
    '''
    Finalize the <order>-th list, and
    Redirect to the next list of questions for <query_id>
    '''
    Schedule.finalize(g.user.user_id, query_id, order)
    schedule = Schedule.find_next(g.user.user_id, query_id)
    if schedule is not None:
        return redirect(url_for('serp',
            query_id=query_id, order=schedule.order))
    else:
        Status.finalize(g.user.user_id, query_id)
        query = Query.find(query_id)
        return render_template('finish.html', query=query)

@app.route('/over')
def over():
    '''
    Show the over page
    '''
    return render_template('over.html')

def _questions_post(query_id):
    '''
    Update the evaluations based on the posted data
    '''
    newevals = request.json.get("evaluations")
    newevals = {e["question_id"]: e["evaluation"] for e in newevals}
    scf = SessionContextFactory()
    with scf.create() as session:
        evaluations = session.query(Evaluation)\
            .filter(Evaluation.query_id == query_id,
            Evaluation.user_id == g.user.user_id,
            Evaluation.question_id.in_(list(newevals.keys()))).all()
        evaluations = {e.question_id: e for e in evaluations}
        for question_id in newevals:
            evaluations[question_id].vote = newevals[question_id]
        session.commit()

def _process_questions(questions, evaluations):
    '''
    Convert questions and evaluations to dict
    '''
    for q in questions:
        q.updated_at = q.updated_at.strftime("%Y/%m/%d %H:%M:%S")
    questions = [{a: getattr(q, a) for a in q.ORDERED_ATTRS}
        for q in questions]
    for q in questions:
        q["evaluation"] = evaluations[q["question_id"]]
    return questions

def _order_questions(question_ids, questions):
    '''
    Order questions in the oder of question_ids
    '''
    questions = {q["question_id"]: q for q in questions}
    return [questions[qid] for qid in question_ids]

@app.before_request
def get_user_cookie():
    '''
    Set a user in the cookie to g.user
    '''
    user_id = request.cookies.get('user_id')
    user = User.find(user_id)
    g.user = user

@app.after_request
def set_user_cookie(response):
    '''
    Create a new user and set it to the cookie
    '''
    if g.user is None:
        user = User.create()
        response.set_cookie('user_id', value=str(user.user_id))
    return response
