#!/bin/bash
set -e
sudo cp ~/CamCan/CameraWebServer/cancamera-flask.service /etc/systemd/system/
sudo cp ~/CamCan/CameraWebServer/cancamera-kiosk.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cancamera-flask cancamera-kiosk
sudo systemctl restart cancamera-flask
sleep 5
curl http://localhost:5000/health
cp ~/CamCan/CameraWebServer/autostart ~/.config/lxsession/LXDE-pi/autostart