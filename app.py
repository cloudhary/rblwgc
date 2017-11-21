import random
from flask import Flask, redirect, url_for, render_template, request
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

@app.route('/')
def homepage():
    return redirect(url_for('training'))

@app.route('/training')
def training():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
    image_ids=['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2', 's1', 's2']
    image_1 = random.choice(image_ids)
    image_2 = random.choice([x for x in image_ids if x != image_1])
    return render_template('training.html', time=the_time,
        image_1=image_1, image_2=image_2,
        options=["Not at all!", "Not too sure..", "Definitely!"])

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    image_ids=['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2', 's1', 's2']
    image_1 = random.choice(image_ids)
    image_2 = random.choice([x for x in image_ids if x != image_1])
    return render_template('classify.html',
        image_1=image_1, image_2=image_2,
        options=["Not at all!", "Not too sure..", "Definitely!"])

@app.route('/submit', methods=['POST'])
def submit():
    print request.form['classification']
    return redirect(url_for('classify'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
