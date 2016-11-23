from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    import openliveq as olq
    q = olq.Question()
    cm = olq.ClickModel.estimate
    return render_template('index.html', msg=str(q) + str(cm))

@app.route('/serp/<query_id>')
def serp(query_id):
    import openliveq as olq
    from openliveq.db import SessionContextFactory
    scf = SessionContextFactory()
    with scf.create() as session:
        questions = session.query(olq.Question).\
            filter(olq.Question.query_id == query_id).\
            limit(10).all()
    return render_template('serp.html', questions=questions)
