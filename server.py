from flask import Flask, url_for, render_template, request
import os
import random
import requests
from operator import xor
import json
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
        print("The following information is stored in the database")
        print("MAC:")
        print(MAC)
        print("C1")
        print(C1)
        print("R1")
        print(R1)
        print("C2")
        print(C2)
        print("R2")
        print(R2)
        print("C3")
        print(C3)
        print("R3")
        print(R3)
        db_user.session.add(user)
        db_user.session.commit()
        return "information is added to the database"
    return "Not a post request"

@app.route('/exchange1',methods=["GET", "POST"])
def exchange1():
    if request.method == 'POST':
        MAC1 = request.form['MAC']
        user = User.query.filter_by(MAC=MAC1).first()
        C1 = user.C1
        C2 = user.C2
        C3 = user.C3
        R1 = user.R1
        R2 = user.R2
        R3 = user.R3
        nonce =  random.randrange(0,65535)
        print("nonce generated")
        print(nonce)
        print(int("{0:b}".format(nonce)))
        user.nonce = str(nonce)
        print("C1")
        print(C1)
        print("{0:b}".format(int(C1)))
        print("R1")
        print(R1)
        print("C2")
        print(C2)
        print("{0:b}".format(int(C2)))
        print("R2")
        print(R2)
        print("{0:b}".format(int(R2)))
        print("C3")
        print(C3)
        print("R3")
        print(R3)
        print("{0:b}".format(int(R3)))
       
        db_user.session.commit()
        R3_ = nonce ^ int(R3)
        R2_ = nonce ^ int(R2)
        C1_ = nonce  ^ int(C1)
        C2_ = nonce  ^ int(C2)
        print("C1_")
        print(C1_)
        print("C2_")
        print(C2_)
        print("R2_")
        print(R2_)
        print("R3_")
        print(R3_)

        jsony = json.dumps({'R3_':R3_,'R2_':R2_,'C1_':C1_,'C2_':C2_,'C3':C3})
        print("data sent to client after first exchange")
        print(jsony)
        return str(jsony)
    return "Not a POST Request"

@app.route('/exchange2',methods=["GET", "POST"])
def exchange2():
    if request.method == 'POST':
        MAC = request.form['MAC']
        R1new_ = request.form['R1new_']
        R2new_ = request.form['R2new_']
        R3new_ = request.form['R3new_']
        R1_ = request.form['R1_']
        Hclient = request.form['Hclient']
        user = User.query.filter_by(MAC=MAC).first()
        R1 = user.R1
        nonce = int(user.nonce)
        print("nonce")
        print(nonce)
        print("R1_")
        print(R1_)
        print("R1")
        print(R1)
        #if int(R1) != (int(nonce) ^ int(R1_)):
        #    return "False1"
        R1new = str(nonce ^ int(R1new_))
        R2new = str(nonce ^ int(R2new_))
        R3new = str(nonce ^ int(R3new_))
        print("R1new")
        print(R1new)
        print("R2new")
        print(R2new)
        print("R3new")
        print(R3new)
        hash_value = int(R1new) | int(R2new) | int(R3new) | int(R1)
        print("hash")
        print(hash_value)
        #if hash_value != int(Hclient):
        #    return "False2"
        user.C1 = str(int(user.C1) ^ int(user.C3))
        user.C2 = str(int(user.C2) ^ int(user.C3))
        user.C3 = str(int(user.nonce) ^ int(user.C3))
        user.R1 = R1new
        user.R2 = R2new
        user.R3 = R3new
        db_user.session.commit()
        print("C1new")
        print(user.C1)
        print("C2new")
        print(user.C2)
        print("C3new")
        print(user.C3)
        jsony = json.dumps({'password':str(xor(int(password),nonce))})
        return str(jsony)
    return "Not aaaaaaaa post request"



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
