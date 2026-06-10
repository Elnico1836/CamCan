# CamCan

Sistema embebido de clasificación de residuos sólidos mediante visión por computadora e inteligencia artificial, desarrollado sobre hardware de bajo costo (ESP32-S3 y Raspberry Pi).

---

## Descripción

CamCan integra un modelo de clasificación de imágenes con un sistema embebido para determinar, en tiempo real, el tipo de residuo capturado por una cámara y orientar su disposición en una de tres categorías:

- Caneca blanca — residuos reciclables
- Caneca negra — residuos no reciclables
- Caneca verde — residuos orgánicos

El sistema opera de forma completamente local, sin dependencia de servicios en la nube.

---

## Arquitectura

El flujo de procesamiento sigue la siguiente secuencia:

```
ESP32-CAM → Servidor web embebido → Navegador (kiosk)
    → Backend Flask → Modelo Keras (.h5)
    → Respuesta JSON → Retroalimentación visual (LEDs + pantalla)
```

La imagen es capturada por el ESP32-S3, transmitida en base64 al backend Flask que corre en la Raspberry Pi, procesada por el modelo de inteligencia artificial, y el resultado se refleja tanto en la interfaz táctil como en los LEDs físicos del dispositivo.

---

## Modelo de inteligencia artificial

- Arquitectura base: MobileNetV2 con transfer learning
- Framework: TensorFlow / Keras
- Dimensión de entrada: 224 × 224 píxeles (RGB)
- Salida: vector de probabilidades para tres clases

```json
{
  "index": 0,
  "probabilidades": [0.85, 0.10, 0.05]
}
```

El modelo fue entrenado sobre un dataset propio de residuos domésticos e industriales comunes en el contexto local.

---

## Backend (Flask)

### POST /predict

Recibe una imagen codificada en base64, la preprocesa y retorna la clasificación del modelo.

Entrada:
```json
{ "imagen": "" }
```

Salida:
```json
{ "index": 1, "probabilidades": [0.10, 0.80, 0.10] }
```

### GET /predict

Endpoint de diagnóstico. Retorna `{ "status": "Servidor activo" }`.

---

## Hardware

|
 Componente 
|
 Función 
|
|
---
|
---
|
|
 ESP32-S3 con cámara 
|
 Captura de imagen y servidor web embebido 
|
|
 Raspberry Pi 
|
 Ejecución del backend Flask y la interfaz kiosk 
|
|
 Pantalla táctil 7" 
|
 Interfaz de usuario 
|
|
 Pantalla OLED (I2C) 
|
 Visualización de IP y QR de acceso 
|
|
 LEDs (GPIO 45, 47, 48) 
|
 Retroalimentación física por categoría 
|

---

## Estructura del proyecto

```
CameraWebServer/
├── CameraWebServer.ino      # Firmware ESP32
├── app_httpd.cpp            # Servidor HTTP embebido
├── camera_index.html        # Interfaz web del ESP32
├── camera_pins.h            # Configuración de pines de cámara
├── app.py                   # Backend Flask (Raspberry Pi)
├── clasificador_canecas.h5  # Modelo entrenado
├── modelo.py                # Script de entrenamiento
├── residuos.py              # Carga y procesamiento del dataset
└── partitions.csv           # Configuración de memoria del ESP32
```

---

## Instalación

**Backend (Raspberry Pi)**

```bash
pip install flask flask-cors pillow numpy tensorflow
python app.py
```

**Firmware (ESP32)**

1. Abrir `CameraWebServer.ino` en Arduino IDE
2. Configurar las credenciales WiFi
3. Seleccionar la placa ESP32-S3 y subir el firmware
4. El dispositivo generará un QR con su IP local en la pantalla OLED

---

## Limitaciones conocidas

- El modelo clasifica un único objeto por captura; escenas con múltiples residuos producen resultados poco fiables.
- El rendimiento depende directamente de la calidad y representatividad del dataset de entrenamiento.
- La iluminación del entorno afecta la precisión de la clasificación.

---

## Líneas de trabajo futuras

- Detección de múltiples objetos con arquitecturas tipo YOLO
- Recolección de estadísticas de uso para análisis de patrones de disposición
- Mecanismo físico de separación automatizada acoplado al sistema de clasificación

---

## Autor

Nicolás Alfonso Alvarado Medina — [github.com/Elnico1836](https://github.com/Elnico1836)

---

*Proyecto de carácter educativo.*
