from pathlib import Path
from flask import Flask, render_template, request, Markup
from flask_cors import CORS
import firebase_admin
from firebase_admin import firestore
import math
from blockchain import Blockchain, Transaction


# Sets up the Flask application
app = Flask(__name__)
app.secret_key = 'Secret Key 123'
tasks_data = {}
CORS(app)
cred_obj = firebase_admin.credentials.Certificate(
    Path(__file__).parent / 'nft-finex-firebase-adminsdk-ke1a6-700f704fe4.json')
default_app = firebase_admin.initialize_app(cred_obj)
blockchain = Blockchain()

@app.route("/", methods=["GET"])
def return_home():
    return render_template('index.html')

@app.route("/setupfirebase", methods=["POST"])
def make_database_from_info():
    name, id, photoURL = request_fields_from_form()
    db = firestore.client()
    doc_ref = db.collection(u'data').document(id)
    doc = doc_ref.get()
    if not doc.exists:
        data = {
            u'name':name,
            u'photoURL': photoURL,
            u'coins': 100,
            u'nft': [],
            u'achievements':[],
            u'courses':[],
            u'current_course':0,
            u'conv_rate':10,
        }
        doc_ref.set(data)
    return "Made Database"

def request_fields_from_form():
    name = request.form["name"]
    id = request.form["id"]
    photoURL = request.form["photoURL"]
    return name, id, photoURL

@app.route("/nft_menu/<id>", methods=['GET'])
def getnfts(id):
    existing_data = get_dict_for_document_and_collection(id, 'data')
    if not existing_data['conv_rate']:
        conv_rate = 10
    else:
        conv_rate = int(existing_data['conv_rate'])
    nfts= (Path(__file__).parent / 'static' / 'images' / 'NFT').glob('*.jpg')
    nft_data = []
    for nft in nfts:
        name = nft.name
        price = round(math.sin(int(name.split('.')[0][3:])) * 30 + 40)
        nft_data.append((name, price))
    return render_template("menu.html", data=nft_data, conv=conv_rate)

@app.route("/add_course_money", methods=['POST'])
def add_course_money():
    '''Displays home page'''
    if request.method == 'POST':
        id = request.form['id']
        existing_data = get_dict_for_document_and_collection(id, 'data')
        course = request.form['course']
        courses_done = existing_data['courses']
        if not courses_done:
            courses_done = []
        new_money = int(existing_data['coins']) + 300
        courses_done.append(course[1:])
        courses_done = list(set(courses_done)) # Remove duplicate entries
        task_list = sorted(tasks_data.keys())
        task_no = task_list.index(course) + 1
        db = firestore.client()
        doc_ref = db.collection(u'data').document(id)
        data = {
            u'coins': new_money,
            u'courses': courses_done,
            u'current_course': task_no
        }
        doc_ref.set(data,merge=True)
        if task_no >= len(task_list):
            return "You have done all the courses!"
        return f"You have unlocked a new course: {task_list[task_no][1:]}. We have added a 300 FEX to your account as a bonus!"

@app.route('/profile/<id>', methods=['GET'])
def serve_profile(id):
    existing_data = get_dict_for_document_and_collection(id, 'data')
    print(existing_data)
    return render_template("profile.html", data=existing_data)

@app.route('/buy_nft', methods=['POST'])
def buy_nft():
    id = request.form['id']
    existing_data = get_dict_for_document_and_collection(id, 'data')
    price = request.form['price']
    nft = request.form['nft']
    existing_nfts=existing_data['nft']
    if not existing_nfts:
        existing_nfts = []

    if int(existing_data['coins']) >= int(price):
        new_money = int(existing_data['coins']) - int(price) 
        existing_nfts.append(str(nft))
        db = firestore.client()
        doc_ref = db.collection(u'data').document(id)
        data = {
            u'coins': new_money,
            u'nft': existing_nfts,
        }
        doc_ref.set(data,merge=True)
        transaction = Transaction("Owner", id, nft)
        blockchain.add_transactions([transaction])
        return(f"NFT bought successfully. New balance = {new_money} FEX")
    else:
        return("Not enough money!")

def get_dict_for_document_and_collection(document, collection):
    db = firestore.client()
    doc_ref = db.collection(collection).document(document)
    doc = doc_ref.get()
    existing_data = doc.to_dict()
    return existing_data

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

@app.route("/tasks/<id>", methods=['GET'])
def tasks(id):
    '''Displays course page'''
    existing_data = get_dict_for_document_and_collection(id, 'data')
    if not existing_data['current_course']:
        task_no = 0
    else:
        task_no = int(existing_data['current_course'])
    task_list = sorted(tasks_data.keys())
    if task_no >= len(task_list):
        return render_template("congratulations.html")
    key = task_list[task_no]
    return render_template("tasks.html", course=key, desc=tasks_data[key])

@app.route("/see_blockchain")
def see_blockchain():
    return Markup(blockchain.display().replace('\n', '<br>'))

@app.route("/change_conv", methods=['POST'])
def change_conv():
    '''Displays home page'''
    if request.method == 'POST':
        id = request.form['id']
        existing_data = get_dict_for_document_and_collection(id, 'data')
        mult = request.form['mult']
        conv_rate = existing_data['conv_rate']
        if not conv_rate:
            conv_rate = 10
        new_rate = int(conv_rate) * float(mult)
        db = firestore.client()
        doc_ref = db.collection(u'data').document(id)
        data = {
            u'conv_rate': new_rate,
        }
        doc_ref.set(data,merge=True)
        return f"Now the convertion rate is 1$ = {round(new_rate, 2)} FEX."

def get_tasks():
    for file in sorted((Path(__file__).parent / 'tasks').glob('*.txt')):
        # Ensure users can't input to files or it will lead to server-side XSS
        tasks_data[file.stem] = Markup(open(file).read().replace('\n', '<br>'))

if __name__ == "__main__":
    get_tasks()
    app.run(debug = True)

