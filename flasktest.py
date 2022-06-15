from flask import Flask, Response, request
import ardSerial as ard
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():

    with open("index.html") as f:
        return Response(f.read(), mimetype="text/html")


@app.route('/ctrl', methods=['GET'])
def forward():
    cmd = request.args.get('cmd')
    try:
        ard.wrapper([cmd, 1])
        return "👍"
    except:
        return "👎"

app.run()
