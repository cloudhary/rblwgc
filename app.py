from flask import Flask
from datetime import datetime
app = Flask(__name__)

@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")

    return """
    <head>
        <title>Raffles Banded Langur classifications</title>
    </head>
    <body>
        <h1>Hello passionate Raffles Banded Langur volunteer!</h1>
        <p>It is currently {time}.</p>

        <img src="http://loremflickr.com/600/400">
        <img src="http://loremflickr.com/600/400">
        <p>Are these two photos of the same langur? </p>
        <input type="button" value="Not the same Langur">
        <input type="button" value="I'm not certain">
        <input type="button" value="Definitely the same Langur!">
    </body>
    """.format(time=the_time)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
