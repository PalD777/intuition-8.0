from pathlib import Path
from flask import Flask, jsonify, render_template, request, session


# Sets up the Flask application
app = Flask(__name__)
app.secret_key = 'Secret Key 123'


@app.route("/", methods=['GET'])
def home():
    '''Displays home page'''
    return render_template("index.html")

@app.route("/form", methods=['GET'])
def form():
    '''Displays form page'''
    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
