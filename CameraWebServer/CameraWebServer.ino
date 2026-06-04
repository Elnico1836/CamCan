#include <WiFi.h>
#include "esp_camera.h"
#include <WebServer.h>

#define CAMERA_MODEL_ESP32S3_EYE
#include "camera_pins.h"

// WIFI
const char* ssid = "CamCan_AP";
const char* password = "nicopro123";

// LEDs
#define LED_BLANCA 45
#define LED_NEGRA 47
#define LED_VERDE 48

WebServer server(81);

void handleCapture();
void handleStream();
void handleLedOn();
void handleLedOff();

void setup() {
  Serial.begin(921600);

  pinMode(LED_BLANCA, OUTPUT);
  pinMode(LED_NEGRA, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);

  digitalWrite(LED_BLANCA, LOW);
  digitalWrite(LED_NEGRA, LOW);
  digitalWrite(LED_VERDE, LOW);

  camera_config_t config;

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;

  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;

  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;

  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;

  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;

  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 12;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 15;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);

  if (err != ESP_OK) {
    Serial.printf("Error cámara: 0x%x\n", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();

  s->set_vflip(s, 1);
  s->set_brightness(s, 1);
  s->set_saturation(s, 0);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect(true, true);
  delay(1000);

  WiFi.begin(ssid, password);

while (true) {
    wl_status_t st = WiFi.status();

    Serial.print("Estado WiFi: ");
    Serial.println(st);

    if (st == WL_CONNECTED) {
        Serial.println("CONECTADO!");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
        break;
    }

    delay(1000);
}

  Serial.print("La direcciòn del MAC del ESP32 es: ");
  Serial.println(WiFi.macAddress());

  // RUTAS DEL SERVIDOR
  server.on("/capture", HTTP_GET, handleCapture);
  server.on("/stream", HTTP_GET, handleStream); // <-- 2. CAMBIO: Vinculamos la ruta /stream para que la use Python

  server.on("/led_on", HTTP_GET, handleLedOn);
  server.on("/led_off", HTTP_GET, handleLedOff);

  server.begin();

  Serial.println("Servidor iniciado");
}

void loop() {
  server.handleClient();
}

// <-- 3. CAMBIO: Añadimos la lógica que genera el flujo de video continuo (MJPEG)
void handleStream() {
  WiFiClient client = server.client();
  
  // Enviamos la cabecera HTTP indicando transferencia de imágenes sin fin
  client.print("HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n");
  
  while (client.connected()) {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      delay(10);
      continue;
    }
    
    // Estructura obligatoria para cada cuadro del flujo
    client.print("--frame\r\nContent-Type: image/jpeg\r\nContent-Length: " + String(fb->len) + "\r\n\r\n");
    client.write(fb->buf, fb->len);
    client.print("\r\n");
    
    esp_camera_fb_return(fb);
    delay(25); // Control de FPS para mantener la estabilidad del ESP32 y la red
  }
}

void handleCapture() {
  camera_fb_t *fb = esp_camera_fb_get();

  if (!fb) {
    server.send(500, "text/plain", "Error cámara");
    return;
  }

  WiFiClient client = server.client();

  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: image/jpeg");
  client.println("Content-Length: " + String(fb->len));
  client.println("Access-Control-Allow-Origin: *");
  client.println();

  client.write(fb->buf, fb->len);

  esp_camera_fb_return(fb);
}

void handleLedOn() {
  if (!server.hasArg("pin")) {
    server.send(400, "text/plain", "Falta pin");
    return;
  }
  int pin = server.arg("pin").toInt();
  digitalWrite(pin, HIGH);
  server.send(200, "text/plain", "LED encendido");
}

void handleLedOff() {
  if (!server.hasArg("pin")) {
    server.send(400, "text/plain", "Falta pin");
    return;
  }
  int pin = server.arg("pin").toInt();
  digitalWrite(pin, LOW);
  server.send(200, "text/plain", "LED apagado");
}