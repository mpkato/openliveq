from flask import (Flask, render_template, redirect, url_for, 
    jsonify, request, g)
import json
import openliveq as olq
from web.query import Query
from web.user import User
from web.user_log import UserLog
from web.schedule import Schedule
from web.status import Status
from web.evaluation import Evaluation
from openliveq.db import SessionContextFactory

app = Flask(__name__)

MAX_ASSIGNMENT = 5
MAX_TIME_INTERVAL = 1800 # 30min

@app.route('/')
def index():
    return redirect(url_for('start'))

@app.route('/start')
def start():
    Status.cleanup(MAX_TIME_INTERVAL)
    query_id = Status.find(g.user.user_id, MAX_ASSIGNMENT)
    if query_id is not None:
        # there is a query available
        Status.init(g.user.user_id, query_id)
        schedule = Schedule.find_next(g.user.user_id, query_id)
        if schedule is not None:
            # there is a schedule available
            return redirect(url_for('serp',
                query_id=query_id, order=schedule.order))
        else:
            # there is no schedule for this query
            # move to the next query
            return redirect(url_for('next', query_id=query_id))
    else:
        # there is no available query
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

@app.route('/next/<query_id>/')
@app.route('/next/<query_id>/<order>')
def next(query_id, order=None):
    '''
    Finalize the <order>-th list, and
    Redirect to the next list of questions for <query_id>
    '''
    if order is not None:
        # finalize a schedule
        Schedule.finalize(g.user.user_id, query_id, order)
    schedule = Schedule.find_next(g.user.user_id, query_id)
    if schedule is not None:
        # use the next schedule
        return redirect(url_for('serp',
            query_id=query_id, order=schedule.order))
    else:
        # show finish page for this query
        Status.finalize(g.user.user_id, query_id)
        code = UserLog.generate_code(g.user.user_id, query_id)
        query = Query.find(query_id)
        return render_template('finish.html', query=query, code=code)

@app.route('/over')
def over():
    '''
    Show the over page
    '''
    return render_template('over.html')

@app.route('/api/<query_id>/<order>', methods=['POST', 'GET'])
def questions(query_id, order):
    '''
    GET: Return the <order>-th list of questions for <query_id>
    POST: Update the evaluations based on the posted data and do the same as GET
    '''
    user_id = g.user.user_id
    if request.method == 'POST':
        newevals = request.json.get("evaluations")
        Evaluation.update(query_id, user_id, newevals)

    questions = Evaluation.find_questions(user_id, query_id, order)
    return jsonify(questions)

@app.before_request
def get_user_cookie():
    '''
    Set a user in the cookie to g.user
    '''
    user_id = request.cookies.get('user_id')
    user = User.find(user_id)
    g.user = user

    if request.path != '/' and user is None:
        return redirect(url_for('index'))

    if user is not None:
        UserLog.create(user.user_id, request.path)

@app.after_request
def set_user_cookie(response):
    '''
    Create a new user and set it to the cookie
    '''
    if g.user is None:
        user = User.create()
        response.set_cookie('user_id', value=str(user.user_id))
    return response
