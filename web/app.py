from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    import openliveq as olq
    q = olq.Question()
    return render_template('index.html', msg=str(q))
