import threading
from time import sleep
from flask import Flask, Response, request, redirect, render_template, url_for
import zmq

context = zmq.Context()

"""
Important, the sockets subsribe and publishes one to many, many to one. 
Therefore indentifier are needed when sending things over the sockets. Like if you want to talk to dog 1 u need D1, dog 2: D2 in the string being sent
The same goes for the other direction, make sure the "dogs" sends an identifier when trying to send information with Dog 1:D1, Dog 2:D2
"""
# TODO: maby move sockets and threading stuff to its own files for structure
# Try to bind as many as possible in the server, static ip will always be 192.168.137.1 as long as the server is runned on the same computer hosting the hotspot
#dog 1 serial socket
sub_sock_daemon = context.socket(zmq.SUB)
sub_sock_daemon.connect('tcp://192.168.137.1:2276') #Can't bind this one in the server, it also needs to connect in auto.py and if sub is the one to bind another sub can't connect, and it needs to connect to the other dog aswell
sub_sock_daemon.setsockopt_string(zmq.SUBSCRIBE, '')

# Bind the socket for communication to the clients (Pi:s, dogs whatever)
pub_sock_pi = context.socket(zmq.PUB)
pub_sock_pi.bind('tcp://192.168.137.1:2273')

# Might need to change this one to connect instead, i think....!, will be same problem as the first socket... but not certain on this one!
# TODO: "make sure it works"
sub_sock_alerts = context.socket(zmq.SUB)
sub_sock_alerts.bind('tcp://192.168.137.1:2274')
sub_sock_alerts.setsockopt(zmq.SUBSCRIBE, b'')

xsub_sock = context.socket(zmq.XSUB)
xpub_sock = context.socket(zmq.XPUB)

# PROXY
xsub_sock.bind('tcp://192.168.137.1:2275')
xpub_sock.bind('tcp://192.168.137.1:2276')

#Logs for dogs, hihi
log_dog1 = ['log start']
log_dog2 = ['log start']

info_dog_1 = "Offline" # a dog is offline untill a message has been recived from them
info_dog_2 = "Offline" # It only recives a message from the auto script right now, so if it starts in manual it wont sat Operational. 

timer_dog1 = 0
timer_dog2 = 0

def start_proxy():
    zmq.proxy(xsub_sock, xpub_sock)

t4 = threading.Thread(target=start_proxy, daemon=True)

def recive_logs():
    global log_dog1
    global log_dog2
    global info_dog_1
    global info_dog_2
    while True:
        r = sub_sock_daemon.recv().decode('utf-8')
        # add in diffrent logs for dog 1 and dog 2
        if (r.find("D1:") != -1):
            if len(log_dog1) > 10:
                log_dog1.clear()
            log_dog1.append(r.replace('D1:', '').strip()) # Remove the dog 1 tag
        
        if (r.find("D2:") != -1):
            if len(log_dog2) > 10:
                log_dog2.clear()
            log_dog2.append(r.replace("D2:", "").strip()) # Remove the dog 2 tag
        # if it start reciving from daemon it is online, but might not yet have started (since the Daemon starts when the pi starts not when the dog starts)
        print(r)
        if ((info_dog_1 == "Offline") and (r.find("D1:") != -1)):
            info_dog_1 = "Online"
        if ((info_dog_2 == "Offline") and (r.find("D2:") != -1)):
            info_dog_2 = "Online"

t = threading.Thread(target=recive_logs, daemon=True )

def recive_alerts():
    global info_dog_1
    global info_dog_2
    global timer_dog1
    global timer_dog2
    while True:
        r = sub_sock_alerts.recv().decode('utf-8')
        print(r)
        if (r.find("D1: Stuck") != -1):
            info_dog_1 = "Help"
            #timer_dog1 is to check if it went offline (Should many be changed to Online, and let logs decide to toggle 
            # offline in kinda the same way, se comments in the recive_logs function why)
            timer_dog1 += 1
        elif (r.find("D1: Operational") != -1):
            info_dog_1 = "Operational"
            timer_dog1 += 1

        if (r.find("D2: Stuck") != -1):
            info_dog_2 = "Help"
            timer_dog2 += 1
        elif (r.find("D2: Operational") != -1):
            info_dog_2 = "Operational"
            timer_dog2 += 1
        
t2 = threading.Thread(target=recive_alerts, daemon=True )

app = Flask(__name__)

def check_if_dog_offline():
    while True:
        global info_dog_1
        global info_dog_2
        old_timervalue_dog1 = timer_dog1
        old_timervalue_dog2 = timer_dog2

        sleep(17) # Seems like a good value

        # if the value hasnt changed anything in 15 seconds the dog probably stopped, but not for certainty did it go Offline (prob tho, but shoud´ld be handeled by the daemon)
        if(old_timervalue_dog1 == timer_dog1 and (info_dog_1 == "D1: Operational" or info_dog_1 == "D1: Stuck")):
            info_dog_1 = "Online"

        if(old_timervalue_dog2 == timer_dog2 and (info_dog_1 == "D2: Operational" or info_dog_1 == "D2: Stuck")):
            info_dog_2 = "Online"

t3 = threading.Thread(target=check_if_dog_offline, daemon=True )

#Renders the start page from template
@app.route('/')
def index():
    return render_template("index.html", info=info_dog_1, info1="Operational")

# Recives messages from the web and sends it on the command socket and only return gg because lol
@app.route('/ctrl', methods=['GET'])
def ctrl():
    cmd = request.args.get('cmd')
    print(cmd)
    pub_sock_pi.send_string(cmd)
    return "gg"

#Get the live feed, this will probably change i tink
@app.route('/feed')
def feed():
    return redirect('http://192.168.137.105:5000', code=301)

@app.route('/alerts')
def alerts():
    out = ""
    #Dog 1, both dogs might need to update their status at the same time (tho not the biggest chance that it will happen) so out gets added with dogs 2 command too
    if(info_dog_1 == "Help"):
        out = "AR:1"
    elif(info_dog_1 == "Operational"):
        out = "ARD:1"
    elif(info_dog_1 == "Offline"):
        out = "OF:1"
    elif(info_dog_1 == "Online"):
        out = "ON:1"

    #Dog 2
    if(info_dog_2 == "help"):
        out += "AR:2"    
    elif(info_dog_2 == "Operational"):
        out += "ARD:2"
    elif(info_dog_2 == "Offline"):
        out += "OF:2"
    elif(info_dog_2 == "Online"):
        out += "ON:2"

    return Response(out)

#Not the best solution, but it has 2 endpoints depending if you want dog 1 or dog 2:s log. (is decided from the localstorage on the web which one to get)
@app.route('/log1')
def logger():
    out = ''
    for i in reversed(log_dog1):
        out += i
        out += "<br>"
    return Response(out)

#Log 2
@app.route('/log2')
def logger2():
    out = ''
    for i in reversed(log_dog2):
        out += i
        out += "<br>"
    return Response(out)

#Start all necessary threads and runs the web-app
if __name__== "__main__":
    t4.start()
    sleep(20)
    t.start()
    t2.start()
    t3.start()
    app.run(host="0.0.0.0", port="8080")
    