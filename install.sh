#!/usr/bin/bash

sudo cp server.service camera.service /etc/systemd/system/

git submodule init
git submodule update

sudo systemctl enable server
sudo systemctl enable camera

sudo systemctl start server
sudo systemctl start camera
