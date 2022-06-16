from flask import Flask, Response, request
import ardSerial as ard
import subprocess
import os
import cv2
from picamera import PiCamera


camera = PiCamera()
app = Flask(__name__)

def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

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

@app.route('/feed')
def feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__== "__main__":
    app.run(host="0.0.0.0")