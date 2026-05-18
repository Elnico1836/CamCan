from flask_cors import CORS
from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
import io
import base64
import tensorflow as tf

app = Flask(__name__)
CORS(app)

model = tf.keras.models.load_model("clasificador_canecas.h5")

def preprocess(image):
    image = image.resize((224, 224))
    img = np.array(image).astype(np.float32) / 255.0
    return np.expand_dims(img, axis=0)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data or 'imagen' not in data:
            return jsonify({"error": "No se recibió la imagen"}), 400

        img_data = base64.b64decode(data['imagen'])
        image = Image.open(io.BytesIO(img_data)).convert('RGB')

        input_data = preprocess(image)

        output = model.predict(input_data)[0]
        
        index = int(np.argmax(output))

        return jsonify({
            "index": index,
            "probabilidades": output.tolist()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['GET'])
def ping():
    return jsonify({"status": "Servidor activo"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)