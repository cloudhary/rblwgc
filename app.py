import random, os
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'my precious'

url = os.environ.get('DATABASE_URL', None)
if url: app.config['SQLALCHEMY_DATABASE_URI'] = url
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
        return '<Image %r and %r have been classified as %r>' % (self.image_1, self.image_2, self.classification)

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(password)

    def __repr__(self):
        return '<name {}'.format(self.name)

@app.route('/')
def homepage():
    db.create_all()
    if session.get('logged_in') == True:
        return redirect((url_for('training')))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(name=request.form['username']).first()
        if user is not None and bcrypt.check_password_hash(
                user.password, request.form['password']):
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('training'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    session.pop('username', None)
    flash("You were logged out successfully!")
    return redirect(url_for('homepage'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        db.session.add(User(request.form['username'],request.form['email'], request.form['password']))
        db.session.commit()
        session['logged_in'] = True
        session['username'] = request.form['username']
        return redirect(url_for('training'))
    else:
        error = 'Invalid Credentials. Please try again.'
    return render_template('signup.html')

@app.route('/training')
def training():
    if session.get('logged_in') != True:
        return redirect(url_for('login'))
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
    image_ids=['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2', 's1', 's2']
    image_1 = random.choice(image_ids)
    image_2 = random.choice([x for x in image_ids if x != image_1])
    return render_template('training.html', time=the_time,
        image_1=image_1, image_2=image_2,
        options=["Not at all!", "Not too sure..", "Definitely!"])

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if session.get('logged_in') != True:
        return redirect(url_for('login'))
    image_ids=['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2', 's1', 's2']
    image_1 = random.choice(image_ids)
    image_2 = random.choice([x for x in image_ids if x != image_1])
    return render_template('classify.html',
        image_1=image_1, image_2=image_2,
        options=["Not at all!", "Not too sure..", "Definitely!"])

@app.route('/submit', methods=['POST'])
def submit():
    classification = request.form['classification']
    image_1 = request.form['image_1']
    image_2 = request.form['image_2']

    if (db):
        db.session.add(Match(image_1, image_2, classification))
        db.session.commit()
        print Match.query.all()
    return redirect(url_for('classify'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
