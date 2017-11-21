import random, os
from flask import Flask, redirect, url_for, render_template, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', "")
db = SQLAlchemy(app)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_1 = db.Column(db.String(80))
    image_2 = db.Column(db.String(80))
    classification = db.Column(db.String(80))

    def __init__(self, image_1, image_2, classification):
        self.image_1 = image_1
        self.image_2 = image_2
        self.classification = classification

    def __repr__(self):
        return '<Image %r and %r have been classified as %r>' % self.image_1, self.image_2, self.classification

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
    classification = request.form['classification']
    db.session.add(Match("A", "B", classification))
    db.session.commit()
    print Match.query.all()
    return redirect(url_for('classify'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
