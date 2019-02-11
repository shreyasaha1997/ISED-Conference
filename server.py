from flask import Flask, url_for, render_template, request
import os
import random
import requests
from operator import xor

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
project_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(project_dir, "clientdatabase.db"))
db_user = SQLAlchemy(app)

password = 1234567890

class User(db_user.Model):
    MAC = db_user.Column(db_user.String(80), unique=True, nullable=False, primary_key=True)
    C1 = db_user.Column(db_user.String(80), nullable=False)
    R1 = db_user.Column(db_user.String(80), nullable=False)
    C2 = db_user.Column(db_user.String(80), nullable=False)
    R2 = db_user.Column(db_user.String(80), nullable=False)
    C3 = db_user.Column(db_user.String(80), nullable=False)
    R3 = db_user.Column(db_user.String(80), nullable=False)
    nonce = db_user.Column(db_user.String(80))
    def __init__(self, MAC, C1, R1, C2, R2, C3, R3):
        self.MAC = MAC
        self.C1 = C1
        self.R1 = R1
        self.C2 = C2
        self.R2 = R2
        self.C3 = C3
        self.R3 = R3

    def __repr__(self):
        return '<MAC %r>' % self.MAC



@app.route("/")
def hello():
    return render_template('base.html', url_for=url_for, users = User.query.all())

@app.route('/submit_data', methods=["GET", "POST"])
def submit_data():
    if request.method == 'POST':
        MAC = request.form['MAC']
        C1 = request.form['C1']
        R1 = request.form['R1']
        C2 = request.form['C2']
        R2 = request.form['R2']
        C3 = request.form['C3']
        R3 = request.form['R3']
        user = User(MAC, C1, R1, C2, R2, C3,R3)
        db_user.session.add(user)
        db_user.session.commit()
        return "information is added to the database"
    return "Not a post request"

@app.route('/exchange1',methods=["GET", "POST"])
def exchange1():
    if request.method == 'POST':
        MAC = request.form['MAC']
        user = User.query.filter_by(MAC=MAC)
        C1 = user.C1
        C2 = user.C2
        C3 = user.C3
        R1 = user.R1
        R2 = user.R2
        R3 = user.R3
        nonce = random.getrandbits(128)
        user.nonce = nonce
        db_user.session.commit()
        R3_ = xor(nonce,R3)
        R2_ = xor(nonce,R2)
        C1_ = xor(nonce,C1)
        C2_ = xor(nonce,C2)
        return json.dumps({'R3_':R3_,'R2_':R2_,'C1_':C1_,'C2_':C2_,'C3':C3})
    return "Not a POST Request"

@app.route('/exchange2',methods=["GET", "POST"])
def exchange2():
    if request.method == 'POST':
        R1new_ = request.form['R1new_']
        R2new_ = request.form['R2new_']
        R3new_ = request.form['R3new_']
        R1_ = request.form['R1_']
        Hclient = request.form['Hclient']
        MAC = request.form['MAC']
        user = User.query.filter_by(MAC=MAC)
        R1 = user.R1
        nonce = user.nonce
        if R1 != xor(nonce,R1_):
            return False
        R1new = xor(nonce,R1new_)
        R2new = xor(nonce,R2new_)
        R3new = xor(nonce,R3new_)
        hash_value = R1new | R2new | R3new | R1
        if hash_value != Hclient:
            return False
        user.C1 = xor(user.C1, user.C3)
        user.C2 = xor(user.C2, user.C3) 
        user.C3 = xor(user.nonce, user.C3)
        user.R1 = R1new
        user.R2 = R2new
        user.R3 = R3new
        db_user.session.commit()
        return str(xor(password, user.nonce))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
