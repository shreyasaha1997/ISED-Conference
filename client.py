from flask import Flask, url_for, render_template, request
import os
import random
import requests
from operator import xor
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import urllib
from operator import xor
import ssl
# from wireless import Wireless


app = Flask(__name__)

MAC = 'b8:27:eb:51:ae:37'
def PUF(c):
    return 1

@app.route("/")
def homepage():
    return render_template('client_connect.html')

@app.route('/connect', methods=["GET", "POST"])
def connect():
    if request.method == 'POST':
        context = ssl._create_unverified_context()
        post_fields = {'MAC':MAC}
        request1 = Request('0.0.0.0:5000/exchange1/', urlencode(post_fields).encode())
        jsony = urlopen(request1,context=context).read()
        jsony = json.loads(jsony)
        C1_ = jsony['C1_']
        C2_ = jsony['C2_']
        R1_ = jsony['R1_']
        R2_ = jsony['R2_']
        R3_ = jsony['R3_']
        C3  = jsony['C3']
        R3 = PUF(C3)
        nonce = xor(R3,R3_)
        C2 = xor(C2_, nonce)
        R2 = xor(R2_, nonce)
        if R2 != PUF(C2):
            return "Router is not Authentic"
        C1 = xor(nonce, C1_)
        R1 = PUF(C1)
        R1_ = xor(nonce, R1)
        R1new = PUF(xor(C1, C3))
        R2new = PUF(xor(C2, C3))
        R3new = PUF(xor(nonce, C3))
        R1new_ = xor(nonce, R1new)
        R2new_ = xor(nonce, R2new)
        R3new_ = xor(nonce, R3new)
        Hclient = R1new | R2new | R3new | R1
        post_fields = {'R1new_':R1new_,'R2new_':R2new,'R3new_':R3new_,'Hclient':Hclient}
        request1 = Request('http://0.0.0.0:5000/exchange2/', urlencode(post_fields).encode())
        response = urlopen(request1,context=context).read().decode()  
        return str(response)          
    return "not a post request"
                
        
        


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
