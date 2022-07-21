# Server

Webserver for interface / GUI to interact with and control the robotdogs. Built with the Flask framework for python. Also host a ZMQ proxy.
Server uses HTTP and port 8080 by default. Can be edited to run on port 80 with sudo privilages.

# Installation
## Manual
```
$ sudo git clone https://github.com/SommarRobotHund2022/PiServer.git
$ cd PiServer
$ git submodule init
$ git submodule update
$ sudo cp server.service /etc/systemd/system/
$ sudo cp camera.service /etc/systemd/system/
$ sudo systemctl enable server
$ sudo systemctl enable camera
$ sudo systemctl start server
$ sudo systemctl start camera
```
## Auto
```
$ sudo git clone https://github.com/SommarRobotHund2022/PiServer.git
$ cd PiServer
$ chmod +x install.sh
$ sudo ./install.sh
```

# Runing
IP-address will automatically pick the IP-address this machine is currently using.
Important notice!! The PiController dosnt know what ip address the server is currently running must be updated in the config.ini file inside the PiController repo!

$ python app.py