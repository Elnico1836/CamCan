#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
#  CanCamera — Setup Completo Raspberry Pi 5
#  Ejecutar con: sudo bash setup_raspberry.sh
# ═══════════════════════════════════════════════════════════════════════════════
set -e

APP_DIR="/home/elnico1836/cancamera"
USER="elnico1836"

echo "╔═══════════════════════════════════════════════════════╗"
echo "║      CanCamera — Setup Raspberry Pi 5 Kiosko          ║"
echo "╚═══════════════════════════════════════════════════════╝"

# ─── 1. DEPENDENCIAS ────────────────────────────────────────────────────────
echo "[1/7] Instalando dependencias del sistema..."
apt-get update -qq
apt-get install -y -qq \
    python3 python3-pip python3-venv python3-dev \
    chromium-browser xdotool \
    libatlas-base-dev libhdf5-dev \
    libjpeg-dev libpng-dev \
    openbox unclutter \
    xserver-xorg xinit x11-xserver-utils

# ─── 2. CARPETAS ────────────────────────────────────────────────────────────
echo "[2/7] Preparando carpetas..."
mkdir -p "${APP_DIR}/logs"
chown -R ${USER}:${USER} "${APP_DIR}"

# ─── 3. ENTORNO VIRTUAL PYTHON ──────────────────────────────────────────────
echo "[3/7] Creando entorno virtual Python..."
if [[ ! -d "${APP_DIR}/venv" ]]; then
    sudo -u ${USER} python3 -m venv "${APP_DIR}/venv"
fi

echo "[3/7] Instalando dependencias Python (puede tardar 10 min)..."
sudo -u ${USER} "${APP_DIR}/venv/bin/pip" install --upgrade pip -q
sudo -u ${USER} "${APP_DIR}/venv/bin/pip" install -q \
    flask flask-cors requests pillow numpy
sudo -u ${USER} "${APP_DIR}/venv/bin/pip" install -q \
    tensorflow==2.16.2 || sudo -u ${USER} "${APP_DIR}/venv/bin/pip" install -q tensorflow

echo "✅ Python listo."

# ─── 4. SERVICIOS SYSTEMD ───────────────────────────────────────────────────
echo "[4/7] Instalando servicios systemd..."

# Flask service
cp "${APP_DIR}/cancamera-flask.service" /etc/systemd/system/
# Kiosk service
cp "${APP_DIR}/cancamera-kiosk.service" /etc/systemd/system/

# ─── 5. OPENBOX CONFIG (bloqueo de teclado) ─────────────────────────────────
echo "[5/7] Configurando Openbox (kiosko bloqueado)..."
mkdir -p /home/${USER}/.config/openbox

cat > /home/${USER}/.config/openbox/autostart << 'AUTOSTART'
# Desactivar salvapantallas y DPMS
xset s off &
xset s noblank &
xset -dpms &
# Ocultar cursor si inactivo 3 seg
unclutter -idle 3 -root &
AUTOSTART

cat > /home/${USER}/.config/openbox/rc.xml << 'OBRC'
<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <keyboard>
    <!-- Bloquear atajos que podrían salir del kiosko -->
    <keybind key="A-F4"><action name="Nothing"/></keybind>
    <keybind key="A-Tab"><action name="Nothing"/></keybind>
    <keybind key="Super_L"><action name="Nothing"/></keybind>
    <keybind key="Super_R"><action name="Nothing"/></keybind>
    <keybind key="C-A-t"><action name="Nothing"/></keybind>
    <keybind key="C-A-Delete"><action name="Nothing"/></keybind>
    <keybind key="F11"><action name="Nothing"/></keybind>
    <keybind key="Escape"><action name="Nothing"/></keybind>
  </keyboard>
  <mouse>
    <context name="Root">
      <mousebind button="Right" action="Press">
        <action name="Nothing"/>
      </mousebind>
    </context>
  </mouse>
  <applications>
    <application class="Chromium-browser">
      <fullscreen>yes</fullscreen>
      <maximized>yes</maximized>
      <decor>no</decor>
      <layer>above</layer>
    </application>
  </applications>
</openbox_config>
OBRC

chown -R ${USER}:${USER} /home/${USER}/.config/

# ─── 6. AUTO-LOGIN EN TTY1 ──────────────────────────────────────────────────
echo "[6/7] Configurando auto-login..."
mkdir -p /etc/systemd/system/getty@tty1.service.d/
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf << AUTOLOGIN
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin ${USER} --noclear %I \$TERM
AUTOLOGIN

# .bash_profile del usuario para arrancar X automáticamente en tty1
cat > /home/${USER}/.bash_profile << 'BASHPROFILE'
# Solo en tty1 y si X no está corriendo
if [[ -z $DISPLAY && $(tty) == /dev/tty1 ]]; then
    exec startx /usr/bin/openbox-session -- :0 vt1
fi
BASHPROFILE
chown ${USER}:${USER} /home/${USER}/.bash_profile

# GPU memory para pantalla 7"
if ! grep -q "gpu_mem=128" /boot/config.txt 2>/dev/null; then
    echo "gpu_mem=128" >> /boot/config.txt
fi

# ─── 7. HABILITAR SERVICIOS ─────────────────────────────────────────────────
echo "[7/7] Habilitando servicios..."
systemctl daemon-reload
systemctl enable cancamera-flask.service
systemctl enable cancamera-kiosk.service

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║           ✅ SETUP COMPLETADO                         ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "PASOS SIGUIENTES:"
echo "  1. Edita ${APP_DIR}/app.py → cambia ESP32_IP"
echo "  2. Copia cancamera-flask.service y cancamera-kiosk.service"
echo "     a ${APP_DIR}/ si no están ya ahí"
echo "  3. sudo reboot"
echo ""
echo "Al reiniciar:"
echo "  • Arranca automáticamente Flask + Chromium en modo kiosko"
echo "  • Teclado bloqueado (sin Alt+Tab, sin terminal, etc.)"
echo "  • Para salir: Ctrl+Alt+F2 → login → sudo systemctl stop cancamera-kiosk"
echo ""
