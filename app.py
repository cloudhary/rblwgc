import random
from flask import Flask, redirect, url_for, render_template
from datetime import datetime
app = Flask(__name__)

@app.route('/')
def homepage():
    return redirect(url_for('training'))

@app.route('/training')
def training():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
    image_ids=['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2', 's1', 's2']
    image_1 = random.choice(image_ids)
    image_2 = random.choice(list(set(image_ids) - set(image_1)))
    return render_template('training.html', time=the_time,
        image_1=image_1, image_2=image_2, same=(image_1[0] == image_2[0]),
        options=["Not at all!", "Not too sure..", "Definitely!"])

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
