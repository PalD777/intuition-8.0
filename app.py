from flask import Flask, request, render_template
from flask_cors import CORS
import firebase_admin
from firebase_admin import firestore
import qrcode
import dateutil
from dateutil import parser
from datetime import datetime
import smtplib
import ssl

cred_obj = firebase_admin.credentials.Certificate(
    'reformbar-a4b02-firebase-adminsdk-y0re0-40695dbdf0.json')
default_app = firebase_admin.initialize_app(cred_obj)

app = Flask(__name__, static_url_path='/static')
CORS(app)


@app.route("/setupfirebase", methods=["POST"])
def make_database_from_info():
    todays_date = datetime.today().strftime('%Y-%m-%d')
    dob, email, gender, height, id, id_official, name, payment, photoURL, weight = request_fields_from_form()
    db = firestore.client()

    doc_ref = db.collection(u'customers').document(id)

    data = {
        u'name': name,
        u'dob': dob,
        u'gender': gender,
        u'payment': payment,
        u'height': height,
        u'weight': weight,
        u'drinks': "0",
        u'id_official': id_official,
        u'alcohol': "0",
        u'photoURL': photoURL,
        u'nuisance': "0",
        u'email': email,
        u'drinking_attempts': "0",
        u'date_updated': todays_date,
    }
    doc_ref.set(data)
    return "Made Database"


def request_fields_from_form():
    name = request.form["name"]
    dob = request.form["dob"]
    gender = request.form["gender"]
    payment = request.form["payment"]
    height = request.form["height"]
    weight = request.form["weight"]
    id = request.form["id"]
    id_official = request.form["id_official"]
    photoURL = request.form["photoURL"]
    email = request.form["email"]
    return dob, email, gender, height, id, id_official, name, payment, photoURL, weight


@app.route('/')
def serve_login():
    return render_template("main_page.html")




@app.route('/register')
def serve_register():
    return render_template("index.html")


@app.route('/bar')
def serve_bar():
    return render_template("menu.html")


@app.route('/nft/<variable>', methods=['GET'])
def serve_drinks(variable):
    db = db = firestore.client()
    doc_ref = db.collection(u'customers').document(id)
    data = {
        u'drinks': str(0),
        u'drinking_attempts': str(0),
        u'alcohol': str(0),
        u'date_updated': todays_date,
    }
    doc_ref.set(data, merge=True)
    return render_template("product_description.html", nft=variable)


@app.route('/profile/<id>', methods=['GET'])
def serve_profile(id):
    existing_data = get_dict_for_document_and_collection(id, 'customers')
    return render_template("profile.html", data=existing_data)


@app.route('/details')
def serve_details():
    return render_template("details.html")


@app.route('/management')
def serve_management():
    db = firestore.client()
    doc_ref = db.collection(u'customers').stream()
    all_users = []
    for users in doc_ref:
        all_users.append(users.to_dict())
    return render_template("management.html", users=all_users)


@app.route('/add_drink', methods=['POST'])
def add_drink():
    todays_date = get_todays_date()
    password = "36fb75181c26195f01aff5144aa1464b"
    name = request.form["drink"]
    id = request.form["id"]
    db = firestore.client()
    accepted_nuicances, bac_accepted, days_after_database_refreshes, drinking_attemps_before_email, legal_drinking_age = make_limit_constants()
    doc_ref, drink_data, existing_data = make_existing_data_dicts(
        db,  id, name)
    date = parser.parse(existing_data["dob"])
    date_updated = parser.parse(existing_data["date_updated"])
    now = get_now_time()
    number_of_days = get_days(date_updated, now)
    age = get_age_difference(date, now)
    bac = calculate_bac(float(existing_data["drinks"]), float(
        existing_data["weight"]), existing_data["gender"], alcohol_consumed=float(existing_data["alcohol"])+float(drink_data["alcohol"]))
    if number_of_days > days_after_database_refreshes:
        doc_ref, drink_data, existing_data = flush_database(db, doc_ref, drink_data, existing_data, id, name,
                                                            todays_date)
    if request.form["password"] == password and float(existing_data["nuisance"]) < accepted_nuicances and bac < bac_accepted and float(existing_data["payment"]) > float(drink_data["price"]) and age > legal_drinking_age:
        send_successful_order(doc_ref, drink_data, existing_data)
        return "Successful Order Placed"
    else:
        return_string = handle_unsuccessful_order(accepted_nuicances, age, bac, bac_accepted, doc_ref, drink_data,
                                                  drinking_attemps_before_email, existing_data, legal_drinking_age,
                                                  password)
        return return_string


def handle_unsuccessful_order(accepted_nuicances, age, bac, bac_accepted, doc_ref, drink_data,
                              drinking_attemps_before_email, existing_data, legal_drinking_age, password):
    update_drinking_attempts(doc_ref, existing_data)
    return_string = "Unsuccessful Order"
    if float(existing_data["drinking_attempts"]) > drinking_attemps_before_email:
        message = '''Good evening
We have observed that you have been going out to the bar very often. 
It should be noted that, while drinking in control is acceptable, alcohol intake can lead to a plethora of health issues, including liver failure, hypertension and anxiety.
We highly recommend you visit a counselor or doctor in order to escape this addiction that may be fueling you, both for the sake of your physical and mental well-being. We can assist in reaching out to an anti-addiction counselor who would walk you through transforming your drinking habits for a better future for yourself
If you would like assistance, kindly send a mail to us and we will inform the counselor of the same. 
Thank you Sir/Ma'am
'''
        SUBJECT = "High Number Of Drinking Attempts"

        send_email(existing_data["email"], message, SUBJECT)
    return_string = set_return_string(accepted_nuicances, age, bac, bac_accepted, drink_data, existing_data,
                                      legal_drinking_age, password, return_string)
    return return_string


def set_return_string(accepted_nuicances, age, bac, bac_accepted, drink_data, existing_data, legal_drinking_age,
                      password, return_string):
    if bac > bac_accepted:
        return_string = "Unsuccessful order:  BAC levels too high"
    elif float(existing_data["payment"]) < float(drink_data["price"]):
        return_string = "Unsuccessful order: Not enough money"
    elif age < legal_drinking_age:
        return_string = "Unsuccessful order: Under the legal age of alcohol consumption"
    elif float(existing_data["nuisance"]) >= accepted_nuicances:
        return_string = "Unsuccessful order: Misbehaviour"
    elif request.form["password"] != password:
        return_string = "Unsuccessful order: Wrong Password"
    return return_string


def flush_database(db, doc_ref, drink_data, existing_data, id, name, todays_date):
    data = {
        u'drinks': str(0),
        u'drinking_attempts': str(0),
        u'alcohol': str(0),
        u'date_updated': todays_date,
    }
    doc_ref.set(data, merge=True)
    doc_ref, drink_data, existing_data = make_existing_data_dicts(db, id, name)
    return doc_ref, drink_data, existing_data


def get_days(date_updated, now):
    number_of_days = dateutil.relativedelta.relativedelta(now, date_updated)
    number_of_days = number_of_days.days
    return number_of_days


def get_age_difference(date, now):
    age = dateutil.relativedelta.relativedelta(now, date)
    age = age.years
    return age


def get_now_time():
    now = datetime.utcnow()
    now = now.date()
    return now


def make_limit_constants():
    days_after_database_refreshes = 4
    drinking_attemps_before_email = 4
    legal_drinking_age = 18
    bac_accepted = 0.07
    accepted_nuicances = 1
    return accepted_nuicances, bac_accepted, days_after_database_refreshes, drinking_attemps_before_email, legal_drinking_age


def get_todays_date():
    from datetime import datetime
    todays_date = datetime.today().strftime('%Y-%m-%d')
    return todays_date


def make_existing_data_dicts(db, id, name):
    doc_ref = db.collection(u'customers').document(id)
    return doc_ref, get_dict_for_document_and_collection(name, 'drink'), get_dict_for_document_and_collection(id, 'customers')


def get_dict_for_document_and_collection(document, collection):
    db = firestore.client()
    doc_ref = db.collection(collection).document(document)
    doc = doc_ref.get()
    existing_data = doc.to_dict()
    return existing_data


def send_successful_order(doc_ref, drink_data, existing_data):
    balance = str(float(existing_data["payment"]) - float(drink_data["price"]))
    number_of_drinks = str(float(existing_data["drinks"]) + 1)
    data = {
        u'drinks': number_of_drinks,
        u'drinking_attempts': str(float(existing_data["drinking_attempts"]) + 1),
        u'alcohol': str(float(existing_data["alcohol"]) + float(drink_data["alcohol"])),
        u'payment': balance,
    }
    doc_ref.set(data, merge=True)
    message = f"Good Evening. \nYour order for your drink has been placed. Current Balance: {balance}\nCurrent Number of Drinks: {number_of_drinks}"
    SUBJECT = "Order Successfully Placed"

    send_email(existing_data["email"], message, SUBJECT)


def update_drinking_attempts(doc_ref, existing_data):
    data = {
        u'drinking_attempts': str(float(existing_data["drinking_attempts"]) + 1),
    }
    doc_ref.set(data, merge=True)


def send_email(email, message, SUBJECT):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = 'pogchampvignesh123@gmail.com'
    receiver_email = email
    password = "vigneshisbae123"
    message = message
    message = 'Subject: {}\n\n{}'.format(SUBJECT, message)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def calculate_bac(no_of_drinks, body_weight_in_kg, gender, r=0.55, alcohol_consumed=14.0):
    if gender == 'Male':
        r = 0.68
    return no_of_drinks * alcohol_consumed * 100 / (body_weight_in_kg * r * 1000)


if __name__ == "__main__":
    app.run(debug=True)
