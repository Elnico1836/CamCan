#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
#  CamCan — Setup Raspberry Pi 5  (Conda edition)
#  Ejecutar desde la carpeta del repo:
#    cd ~/CamCan/CameraWebServer
#    sudo bash setup_raspberry.sh
# ═══════════════════════════════════════════════════════════════════════════════
set -e

REPO_DIR="/home/elnico1836/CamCan/CameraWebServer"
USER="elnico1836"
CONDA_ENV_BIN="/home/elnico1836/miniforge3/envs/cancamera/bin"

echo "╔═══════════════════════════════════════════════════════╗"
echo "║      CamCan — Setup Raspberry Pi 5 (Kiosko)          ║"
echo "╚═══════════════════════════════════════════════════════╝"

# ─── 1. DEPENDENCIAS DEL SISTEMA ─────────────────────────────────────────────
echo "[1/5] Instalando dependencias del sistema..."
apt-get update -qq
apt-get install -y -qq \
    chromium-browser \
    unclutter \
    xdotool

# ─── 2. CARPETA DE LOGS ───────────────────────────────────────────────────────
echo "[2/5] Preparando carpeta de logs..."
mkdir -p "/home/${USER}/CamCan/logs"
chown -R ${USER}:${USER} "/home/${USER}/CamCan"

# ─── 3. SERVICIOS SYSTEMD ─────────────────────────────────────────────────────
echo "[3/5] Instalando servicios systemd..."

cp "${REPO_DIR}/cancamera-flask.service" /etc/systemd/system/
cp "${REPO_DIR}/cancamera-kiosk.service" /etc/systemd/system/

systemctl daemon-reload
systemctl enable cancamera-flask.service

# El kiosk service se habilita solo si hay sesión gráfica
systemctl enable cancamera-kiosk.service || true

# ─── 4. AUTOSTART LXDE (alternativa robusta al kiosk service) ─────────────────
echo "[4/5] Configurando autostart LXDE..."
AUTOSTART_DIR="/home/${USER}/.config/lxsession/LXDE-pi"
mkdir -p "${AUTOSTART_DIR}"

cat > "${AUTOSTART_DIR}/autostart" << 'AUTOSTART'
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 3 -root
@bash -c "sleep 8 && chromium-browser --kiosk --disable-infobars --noerrdialogs --disable-session-crashed-bubble --disable-restore-session-state --no-first-run --incognito http://localhost:5000"
AUTOSTART

chown -R ${USER}:${USER} "${AUTOSTART_DIR}"

# ─── 5. AUTOLOGIN GRÁFICO ──────────────────────────────────────────────────────
echo "[5/5] Configurando autologin gráfico..."
# Esto equivale a: sudo raspi-config → System → Boot → Desktop Autologin
if [ -f /etc/lightdm/lightdm.conf ]; then
    sed -i "s/^#autologin-user=.*/autologin-user=${USER}/" /etc/lightdm/lightdm.conf
    sed -i "s/^autologin-user=.*/autologin-user=${USER}/" /etc/lightdm/lightdm.conf
    # Si la línea no existe, agregarla bajo [Seat:*]
    grep -q "^autologin-user=" /etc/lightdm/lightdm.conf || \
        sed -i "/\[Seat:\*\]/a autologin-user=${USER}" /etc/lightdm/lightdm.conf
fi

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║           ✅ SETUP COMPLETADO                         ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "  → sudo reboot"
echo ""
echo "Al reiniciar:"
echo "  • Flask arranca automáticamente (cancamera-flask.service)"
echo "  • Chromium abre CamCan en pantalla completa"
echo "  • Logs en: ~/CamCan/logs/flask.log"
echo ""
echo "Comandos útiles:"
echo "  sudo systemctl status cancamera-flask"
echo "  sudo journalctl -u cancamera-flask -f"
echo "  tail -f ~/CamCan/logs/flask.log"
echo ""
