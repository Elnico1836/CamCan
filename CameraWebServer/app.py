from flask import Flask, Response, send_file, jsonify
import cv2
import numpy as np
import time

app = Flask(__name__)

# CONFIGURACIÓN ÚNICA
ESP32_IP = "192.168.0.25"
ESP32_STREAM_URL = f"http://{ESP32_IP}/stream"

# Inicializar la captura de video nativa por OpenCV conectando al nuevo stream del ESP32
camera = cv2.VideoCapture(ESP32_STREAM_URL)

# Variable global para almacenar el resultado del clasificador de forma limpia
ultima_prediccion = "Procesando..."

def procesar_ia(frame):
    global ultima_prediccion
    try:
        # =====================================================================
        # TU MODELO DE CLASIFICACIÓN (MobileNetV2 / TFLite) VA AQUÍ:
        # 1. Redimensionas el frame (ej. 224x224)
        # 2. Normalizas los datos
        # 3. Invocas al modelo y obtienes el resultado de la clase.
        #
        # Ejemplo:
        #  clase_detectada = mi_modelo.predict(frame_procesado)
        #  ultima_prediccion = clases[np.argmax(clase_detectada)]
        # =====================================================================
        
        # Simulación temporal (Reemplázala con tu modelo real)
        ultima_prediccion = "Organico / Reciclable (Modelo Activo)"
        
        # Mantenemos el frame completamente limpio para proteger la estética visual.
        pass
    except Exception as e:
        print(f"Error en procesamiento de IA: {e}")
    return frame

def generate_frames():
    while True:
        success, frame = camera.read()
        
        if not success:
            print("⚠️ Buscando señal del stream del ESP32... Verifica la IP o conexión.")
            time.sleep(0.5)
            continue

        # Pasar el cuadro por el modelo (actualiza la variable de predicción de fondo)
        frame = procesar_ia(frame)

        # Codificar el cuadro en JPG limpio
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame_bytes +
            b'\r\n'
        )

@app.route('/video/stream')
def video():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/prediction')
def prediction():
    """ Devuelve el estado de la clasificación en JSON. 
        Úsalo en tu index.html con JavaScript para mostrarlo de forma estética. """
    return jsonify({"clase": ultima_prediccion})

@app.route('/status')
def status():
    if camera.isOpened():
        return jsonify({"status": "connected"})
    return jsonify({"status": "disconnected"})

@app.route("/")
def home():
    return send_file("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)