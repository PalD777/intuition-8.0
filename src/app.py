import time
import json
import requests
import qrcode
from pathlib import Path
from flask import Flask, jsonify, render_template, request, session


# Sets up the Flask application
app = Flask(__name__)
app.secret_key = 'Secret Key 123'


@app.route("/", methods=['GET', 'POST'])
def home():
    '''Displays home page and adds items to cart'''
    if request.method == 'POST':
        qty, item_id = request.form.values()
        update_cart([(item_id, qty)], mode='add')
        return ''
    else:
        menu = get_menu()
        return render_template("index.html", menu=menu)


@app.route("/cart", methods=['GET', 'POST'])
def cart():
    '''Display cart and update its contents based on user input'''
    # Initialise cart if not defined
    if 'cart' not in session:
        session['cart'] = {}

    if request.method == 'POST':
        if request.form['action'] == 'save':
            out = update_cart(list(request.form.items()))
            if out is not None:
                return out
        elif request.form['action'] == 'checkout':
            out = update_cart(list(request.form.items()))
            if out is not None:
                return out

            with open(Path(__file__).parent / 'requests.bin', 'a') as f:
                f.write(f'ORDER SEND {json.dumps(session["cart"])}\n')
            session['cart'] = {}

    return render_template("cart.html", cart=generate_cart(), total=find_total_cost())


@app.route("/qr")
def qr():
    '''
    Generate QR code and render page
    Note: Won't work if device on same network
    '''
    try:
        ip = requests.get('https://api.ipify.org').text
        img = qrcode.make(f'http://{ip}:{app.PORT}')
        img.save(Path(__file__).parent / 'static' / 'images' / 'qr.png')
        return render_template('qr.html')
    except requests.exceptions.ConnectionError:
        return """<h1>Internet Not Available</h1>
        <a href='/'>Go back to main page</a>""", 500
# ---- HELPER FUNCTIONS ---- #


def get_menu():
    '''Get menu from JSON file'''
    with open(Path(__file__).parent / 'menu.json') as menu_file:
        return json.load(menu_file)


def generate_cart():
    '''Helper function to add quantity from the cart to items'''
    cart = []
    for item_id, qty in session['cart'].items():
        item = get_item_from_id(item_id)
        item['qty'] = qty
        cart.append(item)
    return cart


def get_item_from_id(item_id):
    '''Helper function to get item from id'''
    menu = get_menu()
    for item in menu:
        if item['id'] == item_id:
            return item
    else:
        return None


def find_total_cost():
    '''Find total cost of order'''
    total = 0
    for item_id, qty in session['cart'].items():
        price = get_item_from_id(item_id)['price']
        total += price * qty
    return total


def update_cart(data, mode='replace'):
    '''Helper function to update the cart based on data passed'''
    if 'cart' not in session:
        session['cart'] = {}

    for item_id, qty in data:
        if item_id == 'action':
            continue
        # Basic Input Validation
        if not qty.isdigit or int(qty) < 0 or get_item_from_id(item_id) is None:
            return """<h1>Invalid Request</h1>
            <a href='/'>Go back to main page</a>""", 400    # 400 = BadRequest
        if mode == 'add':
            qty = session['cart'].get(item_id, 0) + int(qty)
        else:
            qty = int(qty)

        if qty == 0:
            del session['cart'][item_id]
        else:
            session['cart'][item_id] = qty
        session.modified = True     # To tell flask that a mutable object in session was changed
    return None


if __name__ == "__main__":
    app.PORT = 5000
    app.run(port=app.PORT)
