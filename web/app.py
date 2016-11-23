from flask import Flask, render_template, jsonify, request, g
import openliveq as olq
from .query import Query
from .user import User
from .evaluation import Evaluation
from openliveq.db import SessionContextFactory

app = Flask(__name__)

@app.route('/')
def index():
    q = olq.Question()
    cm = olq.ClickModel.estimate
    return render_template('index.html', msg=str(q) + str(cm))

@app.route('/serp/<query_id>')
def serp(query_id):
    scf = SessionContextFactory()
    with scf.create() as session:
        query = session.query(Query).\
            filter(Query.query_id == query_id).first()
    return render_template('serp.html', query=query)

@app.route('/api/questions/<query_id>', methods=['POST', 'GET'])
def questions(query_id):
    if request.method == 'POST':
        questions_post(query_id)

    scf = SessionContextFactory()
    with scf.create() as session:
        questions = session.query(olq.Question)\
            .filter(olq.Question.query_id == query_id)\
            .limit(10).all()
        question_ids = [q.question_id for q in questions]
        evaluations = session.query(Evaluation)\
            .filter(Evaluation.query_id == query_id,
            Evaluation.user_id == g.user.user_id,
            Evaluation.question_id.in_(question_ids)).all()
        evaluations = {e.question_id: e for e in evaluations}
    questions = _process_questions(questions, evaluations)
    return jsonify(questions)

def questions_post(query_id):
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
            if question_id in evaluations:
                evaluations[question_id].vote = newevals[question_id]
            else:
                e = Evaluation(user_id=g.user.user_id, query_id=query_id,
                    question_id=question_id, vote=newevals[question_id])
                session.add(e)
        session.commit()

def _process_questions(questions, evaluations):
    for q in questions:
        q.updated_at = q.updated_at.strftime("%Y/%m/%d %H:%M:%S")
    questions = [{a: getattr(q, a) for a in q.ORDERED_ATTRS}
        for q in questions]
    for q in questions:
        if q["question_id"] in evaluations:
            q["evaluation"] = evaluations[q["question_id"]].vote
        else:
            q["evaluation"] = False
    return questions

@app.before_request
def get_user_cookie():
    user_id = request.cookies.get('user_id')
    user = User.find(user_id)
    g.user = user

@app.after_request
def set_user_cookie(response):
    if g.user is None:
        user = User.create()
        response.set_cookie('user_id', value=str(user.user_id))
    return response
