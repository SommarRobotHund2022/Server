from flask import Flask, Response, request, redirect, render_template
from commands import commands
from thread_socket_handler import ThreadSocketHandler

#global, dont really know how to handle this one if not global
tsh = ThreadSocketHandler()

app = Flask(__name__)

#Renders the start page from template
@app.route('/')
def index():
    return render_template("index.html", info=tsh.info_dog_1, info1 = commands.get("Op"))

# Recives messages from the web and sends it on the command socket and only return gg because lol
@app.route('/ctrl', methods=['GET'])
def ctrl():
    cmd = request.args.get('cmd')
    print(cmd)
    tsh.pub_sock_pi.send_string(cmd)
    return "gg"

#Get the live feed, this will probably change i tink
@app.route('/feed')
def feed():
    return redirect('http://192.168.137.105:5000', code=301)

@app.route('/alerts')
def alerts():
    out = ""
    #Dog 1, both dogs might need to update their status at the same time (tho not the biggest chance that it will happen) so out gets added with dogs 2 command too
    if(tsh.info_dog_1 == commands.get("He")):
        out = "AR:1"
    elif(tsh.info_dog_1 == commands.get("Op")):
        out = "ARD:1"
    elif(tsh.info_dog_1 == commands.get("Off")):
        out = "OF:1"
    elif(tsh.info_dog_1 == commands.get("On")):
        out = "ON:1"
    elif(tsh.info_dog_1 == commands.get("Face")):
        tsh.info_dog_1 = "" #Resets this one here, is needed cuz the reset is taken care from in the frontend, this will mess things upp if removed
        out = "FACE:1"
    elif(tsh.info_dog_1 == commands.get("Au")):
        tsh.info_dog_1 = "" #Resets this one here, is needed cuz the reset is taken care from in the frontend, this will mess things upp if removed
        out = "Auto:"
    elif(tsh.info_dog_1 == commands.get("Ma")):
        tsh.info_dog_1 = "" #Resets this one here, is needed cuz the reset is taken care from in the frontend, this will mess things upp if removed
        out = "Manual:"

    #Dog 2
    if(tsh.info_dog_2 == commands.get("He")):
        out += "AR:2"    
    elif(tsh.info_dog_2 == commands.get("Op")):
        out += "ARD:2"
    elif(tsh.info_dog_2 == commands.get("Off")):
        out += "OF:2"
    elif(tsh.info_dog_2 == commands.get("On")):
        out += "ON:2"
    elif(tsh.info_dog_2 == commands.get("Face")):
        tsh.info_dog_2 = "" #Resets this one here, is needed cuz the reset is taken care from in the frontend, this will mess things upp if removed
        out = "FACE:2"
    elif(tsh.info_dog_2 == commands.get("Au")):
        tsh.info_dog_2 = "" #Resets this one here, is needed cuz the reset is taken care from in the frontend, this will mess things upp if removed
        out = "Auto:"
    elif(tsh.info_dog_2 == commands.get("Ma")):
        tsh.info_dog_2 = "" #Resets this one here, is needed cuz the reset is taken care from in the frontend, this will mess things upp if removed
        out = "Manual:"

    return Response(out)

#Not the best solution, but it has 2 endpoints depending if you want dog 1 or dog 2:s log. (is decided from the localstorage on the web which one to get)
@app.route('/log1')
def logger():
    out = ''
    for i in reversed(tsh.log_dog1):
        out += i
        out += "<br>"
    return Response(out)

#Log 2
@app.route('/log2')
def logger2():
    out = ''
    for i in reversed(tsh.log_dog2):
        out += i
        out += "<br>"
    return Response(out)

#Start all necessary threads and runs the web-app
if __name__== "__main__":
    tsh.run()
    app.run(host="0.0.0.0", port="8080")
    