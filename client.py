from flask import Flask, url_for, render_template, request
import os
import random
import requests
from operator import xor
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from operator import xor
import ssl
# from wireless import Wireless
import json
import requests


import time
import serial
import numpy as np
ser = serial.Serial(              
               port='/dev/ttyUSB1',
               baudrate = 19200,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=1
           )

app = Flask(__name__)

MAC = 'b8:27:eb:04:fb:62'
headers = {
    "content-type": "application/json"
}
def PUF(c):
    ser.flush()
    c1 = int(c)
    c1 = np.uint16(c1)
    print("writing challenge to serial output")
    print(c1)
    ser.write(c1.tobytes())
    ser.flush()
    dummy = np.uint8(5)
    print("sending dummy to serial output")
    print(dummy)
    ser.write(dummy)
    ser.flush()
    # time.sleep(0.4)
    response =ser.readline()
    print("response received")
    print(response.decode("utf-8") )
    response =ser.readline()
    print("response received")
    print(response.decode("utf-8") )
    response =ser.readline()
    print("response received")
    print(response.decode("utf-8") )
    return str(response.decode("utf-8"))

@app.route("/")
def homepage():
    return render_template('client_connect.html')

@app.route('/connect', methods=["GET", "POST"])
def connect():
    if request.method == 'POST':
        context = ssl._create_unverified_context()
        post_fields = {'MAC':MAC}
        
        request1 = Request('http://172.16.12.37:5000/exchange1', urlencode(post_fields).encode())
        jsony = urlopen(request1,context=context).read()
        
        jsony = jsony.decode("utf-8") 
        jsony = json.loads(jsony)
        C1_ = jsony['C1_']
        C2_ = jsony['C2_']
        R2_ = jsony['R2_']
        R3_ = jsony['R3_']
        C3  = jsony['C3']
        R3 = PUF(C3)
        print("R3")
        print(R3)
        nonce = int(R3) ^ int(R3_)
        print("nonce")
        print(nonce)
        C2 = int(C2_) ^ int(nonce)
        print("C2")
        print(C2)
        R2 = int(R2_) ^ int(nonce)
        print("R2")
        print(R2)
        print(PUF(C2))
        #if R2 != PUF(C2):
        #    return "Router is not Authentic"
        C1 = nonce ^ int(C1_)
        R1 = PUF(str(C1))
        R1_ = nonce ^ int(R1)
        print("C1")
        print(C1)
        print("R1")
        print("R1_")
        print(R1)
        print(R1_)
        R1new = PUF(int(C1) ^ int(C3))
        R2new = PUF(int(C2) ^ int(C3))
        R3new = PUF(nonce ^ int(C3))
        R1new_ = nonce ^ int(R1new)
        R2new_ = nonce ^ int(R2new)
        R3new_ = nonce ^ int(R3new)
        print("R1new")
        print(R1new)
        print(R1new_)
        print("R2new")
        print(R2new)
        print(R2new_)
        print("R3new")
        print(R3new)
        print(R3new_)
        Hclient = int(R1new)| int(R2new)| int(R3new)| int(R1)
        post_fields = {'MAC':MAC,'R1new_':str(R1new_),'R2new_':str(R2new_),'R3new_':str(R3new_),'Hclient':str(Hclient),'R1_':str(R1_)}
        print(post_fields)
        request2 = Request('http://172.16.12.37:5000/exchange2', data=urlencode(post_fields).encode())
        response2 = urlopen(request2).read()
        return response2          
    return "not a post request"
                
        
        


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
