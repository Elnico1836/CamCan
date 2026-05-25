#!/bin/bash
set -e

echo "Copiando servicios..."
sudo cp ~/CamCan/CameraWebServer/cancamera-flask.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cancamera-flask
sudo systemctl set-default graphical.target

echo "Configurando autostart labwc..."
mkdir -p ~/.config/labwc
cp ~/CamCan/CameraWebServer/autostart-labwc ~/.config/labwc/autostart

echo "Configurando bash_profile..."
cat > ~/.bash_profile << 'EOF'
if [[ -z $DISPLAY && $(tty) == /dev/tty1 ]]; then
    exec startx /usr/bin/labwc -- :0 vt1
fi
EOF

echo "Reiniciando Flask..."
sudo systemctl restart cancamera-flask
sleep 5
curl http://localhost:5000/health