from pathlib import Path
from flask import Flask, jsonify, render_template, request, session


# Sets up the Flask application
app = Flask(__name__)
app.secret_key = 'Secret Key 123'


@app.route("/", methods=['GET', 'POST'])
def home():
    '''Displays home page'''
    if request.method == 'POST':
        print(list(request.form.items()))
    return render_template("index.html")

@app.route("/form", methods=['GET'])
def form():
    '''Displays form page'''
    return render_template("form.html")

@app.route("/game", methods=['GET'])
def game():
    '''Displays game page'''
    return render_template("gamification.html")

@app.route("/support", methods=['GET'])
def support():
    '''Displays form page'''
    return render_template("support.html")

@app.route("/tasks", methods=['GET'])
def tasks():
    '''Displays form page'''
    return render_template("tasks.html", course = "stonk")
if __name__ == "__main__":
    app.run(debug = True)
