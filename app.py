import threading
from flask import Flask, Response, request, redirect, render_template, url_for
import zmq

context = zmq.Context()

sub_sock = context.socket(zmq.SUB)
sub_sock.connect('tcp://192.168.137.71:2271')
sub_sock.setsockopt_string(zmq.SUBSCRIBE, '')

pub_sock = context.socket(zmq.PUB)
pub_sock.bind('tcp://192.168.137.1:2273')

sub_sock_alerts = context.socket(zmq.SUB)
sub_sock_alerts.bind('tcp://192.168.137.1:2274')
sub_sock_alerts.setsockopt(zmq.SUBSCRIBE, b'')

log = ['log start']

info_dog_1 = "Operational"
info_dog_2 = "Operational"

def d():
    while True:
        r = sub_sock.recv().decode('utf-8')
        log.append(r)

t = threading.Thread(target=d, daemon=True )

def recive_alerts():
    global info_dog_1
    global info_dog_2
    while True:
        r = sub_sock_alerts.recv().decode('utf-8')
        if (r == "Dog 1: stuck"):
            info_dog_1 = "Help"
        elif (r == "Dog 1: Operational"):
            info_dog_1 = "Operational"

        if (r == "Dog 2: stuck"):
            info_dog_2 = "Help"
        elif (r == "Dog 1: Operational"):
            info_dog_2 = "Operational"

t2 = threading.Thread(target=recive_alerts, daemon=True )

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html", info=info_dog_1, info1="Operational")


@app.route('/ctrl', methods=['GET'])
def ctrl():
    cmd = request.args.get('cmd')
    print(cmd)
    pub_sock.send_string(cmd)
    return "gg"

@app.route('/feed')
def feed():
    return redirect('http://192.168.137.105:5000', code=301)

@app.route('/alerts')
def alerts():
    out = "Operational"
    if (info_dog_1 == "Help" and info_dog_2 == "Help"):
        out = "AR:12"
    elif(info_dog_1 == "Help"):
        out = "AR:1"
    elif(info_dog_2 == "help"):
        out = "AR:2"
    elif (info_dog_1 == "Operational" and info_dog_2 == "Operational"):
        out = "ARD:12"
    elif(info_dog_1 == "Operational"):
        out = "ARD:1"
    elif(info_dog_2 == "Operational"):
        out = "ARD:2"

    return Response(out)

@app.route('/log')
def logger():
    out = ''
    for i in reversed(log):
        out += i
        out += "<br>"
    print("sending: ", log)
    return Response(out)

if __name__== "__main__":
    t.start()
    t2.start()
    app.run(host="0.0.0.0", port="8080")
    