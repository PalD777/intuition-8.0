from pathlib import Path
from flask import Flask, jsonify, render_template, request, session, Markup


# Sets up the Flask application
app = Flask(__name__)
app.secret_key = 'Secret Key 123'
tasks_data = {}

class user:
    '''Test class to temp store stuff of db'''
    pass

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

@app.route("/invest", methods=['GET'])
def invest():
    '''Displays form page'''
    return render_template("invest.html")

@app.route("/tasks", methods=['GET'])
def tasks():
    '''Displays form page'''
    key = sorted(tasks_data.keys())[user.task_no]
    return render_template("tasks.html", course = key, desc=tasks_data[key])

def get_tasks():
    for file in sorted((Path(__file__).parent / 'tasks').glob('*.txt')):
        # Ensure users can't input to files or it will lead to server-side XSS
        tasks_data[file.stem] = Markup(open(file).read().replace('\n', '<br>'))

if __name__ == "__main__":
    get_tasks()
    print(tasks_data)
    user.task_no = 0
    app.run(debug = True)
