import random, os
import traceback
import json
import requests
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import exc, func

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'my precious'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

url = os.environ.get('DATABASE_URL', None)
if url: 
    app.config['SQLALCHEMY_DATABASE_URI'] = url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"

db = SQLAlchemy(app)
db.create_all()

@app.route('/flush')
def flushing():
    db.reflect()
    db.drop_all()
    db.create_all()
    return 'OMG db has been flushed!'

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_1 = db.Column(db.String(80))
    image_2 = db.Column(db.String(80))
    classification = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, image_1, image_2, classification, user_id):
        self.image_1 = image_1
        self.image_2 = image_2
        self.classification = classification
        self.user_id = user_id

    def __repr__(self):
        return '<Image %r and %r have been classified as %r by %r>' % (self.image_1, self.image_2, self.classification, self.id)

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    classifications = db.relationship('Match', backref='users', lazy=True)

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
        
        if User.query.filter_by(email=request.form['email']).first() is None and \
            User.query.filter_by(name=request.form['username']).first() is None:

            new_user = User(request.form['username'],request.form['email'], request.form['password'])
            db.session.add(new_user)
            db.session.commit()
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('training'))
        else:
            db.session.rollback()
            flash('Oops! Username ' + request.form['username'] + ' or Email ' + request.form['username'] \
             + ' already exists!', 'error')
    else:
        error = 'Invalid Credentials. Please try again.'
    return render_template('signup.html')

@app.route("/leaderboard")
def leaderboard():
    if session.get('logged_in') != True:
        return redirect(url_for('login'))

    board = db.engine.execute('''
    SELECT users.name, count(match.id) FROM match
    JOIN users on users.id = match.user_id
    GROUP BY users.id
    ORDER BY count(match.id) DESC
    LIMIT 50
    ''')
    user = User.query.filter_by(name=session['username']).first()
    total_count = Match.query.filter_by(user_id=user.id).count()
    return render_template('leaderboard.html', board=board,
                           total_count=total_count)

@app.route("/credits")
def credits():
    if session.get('logged_in') == True:
        user = User.query.filter_by(name=session['username']).first()
        total_count = Match.query.filter_by(user_id=user.id).count()
    else:
        total_count = ''
    return render_template('credits.html', total_count=total_count)

@app.route('/training')
def training():
    if session.get('logged_in') != True:
        return redirect(url_for('login'))
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
    image_ids=['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2', 's1', 's2']
    image_1 = random.choice(image_ids)
    image_2 = random.choice([x for x in image_ids if x != image_1])
    
    # Deal with Invalid Sessions
    try:
        user = User.query.filter_by(name=session['username']).first()
    except:
        return redirect(url_for('logout'))

    if user is None:
        return redirect(url_for('logout'))

    total_count = Match.query.filter_by(user_id=user.id).count()
    return render_template('training.html', time=the_time,
        image_1=image_1, image_2=image_2, total_count=total_count,
        options=["Not at all!", "Not too sure..", "Definitely!"])

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if session.get('logged_in') != True:
        return redirect(url_for('login'))

    # Gather Image Limits
    limit = requests.get("https://s3-ap-southeast-1.amazonaws.com/rblwg/images/meta.json")
    limit  = json.loads(limit.text)['image_count']
    image_ids = list(range(1, int(limit)))
    image_1 = random.choice(image_ids)
    image_2 = random.choice([x for x in image_ids if x != image_1])
    image_1 = "https://s3-ap-southeast-1.amazonaws.com/rblwg/images/image" + '{:05d}'.format(image_1) + ".jpg"
    image_2 = "https://s3-ap-southeast-1.amazonaws.com/rblwg/images/image" + '{:05d}'.format(image_2) + ".jpg"
    image_1 = "http://edge.zimage.io/?url=" + image_1 + "&w=600"
    image_2 = "http://edge.zimage.io/?url=" + image_2 + "&w=600"
    #image_1 = "http://s3-ap-southeast-1.amazonaws.com.rsz.io/rblwg/images/image" + '{:05d}'.format(image_1) + ".jpg?width=600"
    #image_2 = "http://s3-ap-southeast-1.amazonaws.com.rsz.io/rblwg/images/image" + '{:05d}'.format(image_2) + ".jpg?width=600"

    user = User.query.filter_by(name=session['username']).first()
    total_count = Match.query.filter_by(user_id=user.id).count()
    return render_template('classify.html',
        image_1=image_1, image_2=image_2, total_count=total_count,
        options=["Not at all!", "Not too sure..", "Definitely!"])


@app.route('/submit', methods=['POST'])
def submit():
    classification = request.form['classification']
    image_1 = request.form['image_1']
    image_2 = request.form['image_2']

    # Clean URLs
    image_1 = image_1.split("/")[-1].split("&")[0]
    image_2 = image_2.split("/")[-1].split("&")[0]
    user = User.query.filter_by(name=session['username']).first()

    if (db):
        db.session.add(Match(image_1, image_2, classification, user.id))
        db.session.commit()
    return redirect(url_for('classify'))

@app.errorhandler(500)
def internal_error(exception):
    """Show traceback in the browser when running a flask app on a production server.
    By default, flask does not show any useful information when running on a production server.
    By adding this view, we output the Python traceback to the error 500 page.
    """
    trace = traceback.format_exc()
    return("<pre>" + trace + "</pre>"), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
