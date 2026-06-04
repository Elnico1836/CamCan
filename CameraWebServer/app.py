import io
import base64
import logging
import time
import requests
import numpy as np
from flask import Flask, Response, request, jsonify, send_file
from PIL import Image

#IP ESP32
ESP32_IP   = "192.168.4.24"
MODEL_PATH = "clasificador_canecas_compat.keras"

CLASES   = ["Caneca_blanca", "Caneca_negra", "Caneca_verde", "Caneca_fondo"]
IMG_SIZE = (224, 224)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("CanCamera")

model = None

def load_model():
    global model
    try:
        import tensorflow as tf

        @tf.keras.utils.register_keras_serializable()
        class FixedBatchNorm(tf.keras.layers.BatchNormalization):
            def __init__(self, **kwargs):
                kwargs.pop('renorm', None)
                kwargs.pop('renorm_clipping', None)
                kwargs.pop('renorm_momentum', None)
                super().__init__(**kwargs)

        @tf.keras.utils.register_keras_serializable()
        class FixedDense(tf.keras.layers.Dense):
            def __init__(self, **kwargs):
                kwargs.pop('quantization_config', None)
                super().__init__(**kwargs)

        log.info("TensorFlow %s — cargando modelo %s ...", tf.__version__, MODEL_PATH)
        model = tf.keras.models.load_model(
            MODEL_PATH,
            custom_objects={
                "FixedBatchNorm": FixedBatchNorm,
                "FixedDense": FixedDense
            }
        )
        dummy = np.zeros((1, IMG_SIZE[0], IMG_SIZE[1], 3), dtype=np.float32)
        model.predict(dummy, verbose=0)
        log.info("✅ Modelo listo. Clases: %s", CLASES)
    except Exception as e:
        log.error("❌ Error cargando modelo: %s", e)
        model = None

app = Flask(__name__)

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "modelo": model is not None,
        "esp32": ESP32_IP,
        "clases": CLASES,
    })

@app.route("/video/stream")
def video_stream():
    esp32_stream_url = f"http://{ESP32_IP}:81/stream"
    try:
        r = requests.get(esp32_stream_url, stream=True, timeout=10)
        content_type = r.headers.get(
            "Content-Type",
            "multipart/x-mixed-replace; boundary=frame"
        )
        return Response(r.iter_content(chunk_size=4096), content_type=content_type)
    except Exception as e:
        log.warning("Stream proxy error: %s", e)
        return jsonify({"error": f"ESP32 no disponible: {e}"}), 503

@app.route("/capture")
def capture():
    url = f"http://{ESP32_IP}/capture"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            log.warning("ESP32 /capture devolvió status %d", r.status_code)
            return jsonify({"error": "ESP32 capture failed"}), 502
        return Response(r.content, content_type="image/jpeg")
    except Exception as e:
        log.warning("Capture proxy error: %s", e)
        return jsonify({"error": str(e)}), 503

@app.route("/predict", methods=["POST", "GET"])
def predict():
    if request.method == "GET":
        return jsonify({"ok": True, "modelo": model is not None})

    if model is None:
        log.error("Predicción solicitada pero el modelo no está cargado.")
        return jsonify({"error": "Modelo no cargado"}), 503

    data = request.get_json(silent=True) or {}
    imagen_b64 = data.get("imagen")
    if not imagen_b64:
        return jsonify({"error": "Se requiere el campo 'imagen' en base64"}), 400

    try:
        img_bytes = base64.b64decode(imagen_b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        log.warning("Imagen inválida: %s", e)
        return jsonify({"error": f"Imagen inválida: {e}"}), 400

    img_resized = img.resize(IMG_SIZE, Image.LANCZOS)
    arr = np.array(img_resized, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)

    try:
        t0    = time.perf_counter()
        preds = model.predict(arr, verbose=0)[0]
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
    except Exception as e:
        log.error("Error en inferencia: %s", e)
        return jsonify({"error": f"Inferencia fallida: {e}"}), 500

    probs = preds.tolist()
    idx   = int(np.argmax(preds))
    clase = CLASES[idx]
    conf  = float(preds[idx])

    prediccion_list = [
        {"clase": CLASES[i], "confianza": float(preds[i])}
        for i in range(len(CLASES))
    ]

    log.info(
        "→ %s (%.1f%%) | B:%.0f%% N:%.0f%% V:%.0f%% F:%.0f%% | %dms",
        clase, conf * 100,
        probs[0]*100, probs[1]*100, probs[2]*100, probs[3]*100,
        elapsed_ms,
    )

    return jsonify({
        "prediccion":     prediccion_list,
        "probabilidades": probs,
        "index":          idx,
        "clase":          clase,
        "confianza":      conf,
        "tiempo_ms":      elapsed_ms,
    })

@app.route("/led_on")
def led_on():
    pin = request.args.get("pin", "")
    try:
        requests.get(f"http://{ESP32_IP}/led_on?pin={pin}", timeout=3)
        return "ok", 200
    except Exception:
        return "error", 503

@app.route("/led_off")
def led_off():
    pin = request.args.get("pin", "")
    try:
        requests.get(f"http://{ESP32_IP}/led_off?pin={pin}", timeout=3)
        return "ok", 200
    except Exception:
        return "error", 503

if __name__ == "__main__":
    load_model()
    log.info("🚀 Servidor en http://0.0.0.0:5000")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False,
    )