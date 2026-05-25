#!/bin/bash
set -e
sudo cp ~/CamCan/CameraWebServer/cancamera-flask.service /etc/systemd/system/
sudo cp ~/CamCan/CameraWebServer/cancamera-kiosk.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cancamera-flask cancamera-kiosk
sudo systemctl set-default graphical.target
mkdir -p ~/.config/lxsession/LXDE-pi
cp ~/CamCan/CameraWebServer/autostart ~/.config/lxsession/LXDE-pi/autostart
sudo mkdir -p /etc/xdg/lxsession/rpd-x
sudo cp ~/CamCan/CameraWebServer/autostart /etc/xdg/lxsession/rpd-x/autostart
sudo systemctl restart cancamera-flask
sleep 5
curl http://localhost:5000/health