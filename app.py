import threading
from flask import Flask, Response, request, redirect, render_template
import zmq

context = zmq.Context()
req_sock = context.socket(zmq.REQ)
sub_sock = context.socket(zmq.SUB)
sub_sock.connect('tcp://127.0.0.1:2271')
req_sock.connect("tcp://127.0.0.1:2272")
sub_sock.setsockopt_string(zmq.SUBSCRIBE, '')


def d():
    while True:
            print(sub_sock.recv())

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
    req_sock.send_string(cmd)
    return req_sock.recv()

@app.route('/feed')
def feed():
    return redirect('http://localhost:5000', code=301)


if __name__== "__main__":
    t.start()
    app.run(host="0.0.0.0", port="8080")
    