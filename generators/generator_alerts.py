from multiprocessing import context
from time import sleep
import zmq
import random
import socket

context = zmq.Context()

pub_sock_alerts = context.socket(zmq.PUB)
pub_sock_alerts.connect("tcp://" + str(socket.gethostbyname(socket.gethostname())) + ":2274")

"""
Generates diffrent alerts  every 10 sec randomly to see if things work like they should in server
"""
commands = {
    0: "D1: Stuck",
    1: "D2: Stuck",
    2: "D1: Operational",
    3: "D2: Operational",
    4: "D1: Found face!",
    5: "D2: Found face!",
}

def send_face_alert():
    while True:
        n = random.randint(0,5)
        sleep(10)
        print("Sending one alert")
        pub_sock_alerts.send_string(commands[n])

if __name__=="__main__":
    send_face_alert()