from flask import Flask, render_template

# Sets up the Flask application
app = Flask(__name__)
app.secret_key = 'Secret Key 123'

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug = True)