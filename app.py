import threading
from flask import Flask, Response, request, redirect, render_template
import zmq

context = zmq.Context()
req_sock = context.socket(zmq.REQ)
sub_sock = context.socket(zmq.SUB)
sub_sock.connect('tcp://127.0.0.1:2271')
req_sock.connect("tcp://127.0.0.1:2272")
sub_sock.setsockopt_string(zmq.SUBSCRIBE, '')

log = ['log start']


def d():
    while True:
        r = sub_sock.recv().decode('utf-8')
        log.append(r)

t = threading.Thread(target=d, daemon=True )
app = Flask(__name__)


@app.route('/')
def index():
    with open("index.html") as f:
        return Response(f.read(), mimetype="text/html")


@app.route('/ctrl', methods=['GET'])
def ctrl():
    cmd = request.args.get('cmd')
    print('command recv')
    print(cmd)
    req_sock.send_string(cmd)
    return req_sock.recv()

@app.route('/feed')
def feed():
    return redirect('http://192.168.137.105:5000', code=301)

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
    app.run(host="0.0.0.0", port="8080")
    