from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    import openliveq as olq
    q = olq.Question()
    cm = olq.ClickModel.estimate
    return render_template('index.html', msg=str(q) + str(cm))

@app.route('/serp')
def serp():
    import openliveq as olq
    return render_template('serp.html')
