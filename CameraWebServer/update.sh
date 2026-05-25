#!/bin/bash
set -e

echo "Copiando servicios..."
sudo cp ~/CamCan/CameraWebServer/cancamera-flask.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cancamera-flask
sudo raspi-config nonint do_boot_behaviour B2

echo "Configurando arranque X11..."
cat > ~/.bash_profile << 'EOF'
if [[ -z $DISPLAY && $(tty) == /dev/tty1 ]]; then
    exec startx -- :0 vt1
fi
EOF

cat > ~/.xinitrc << 'EOF'
xset s off
xset -dpms
xset s noblank
unclutter -idle 3 -root &
sleep 10
chromium --no-sandbox --kiosk --disable-infobars http://localhost:5000
EOF

echo "Reiniciando Flask..."
sudo systemctl restart cancamera-flask
sleep 5
curl http://localhost:5000/health