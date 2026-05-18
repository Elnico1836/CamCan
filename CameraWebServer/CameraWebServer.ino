#include <WiFi.h>
#include "esp_camera.h"
#include <WebServer.h>

#define CAMERA_MODEL_ESP32S3_EYE
#include "camera_pins.h"

// WIFI
const char* ssid = "RouterFamily";
const char* password = "Luchis12088";

// LEDs
#define LED_BLANCA 45
#define LED_NEGRA 47
#define LED_VERDE 48

WebServer server(80);

void handleJPGStream();
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
    config.jpeg_quality = 15;
    config.fb_count = 2;
    config.xclk_freq_hz = 24000000;
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

  WiFi.begin(ssid, password);

  Serial.print("Conectando WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectado");

  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  server.on("/stream", HTTP_GET, handleJPGStream);

  server.on("/led_on", HTTP_GET, handleLedOn);
  server.on("/led_off", HTTP_GET, handleLedOff);

  server.begin();

  Serial.println("Servidor iniciado");
}

void loop() {
  server.handleClient();
}

void handleJPGStream() {

  WiFiClient client = server.client();

  String response =
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n"
    "Access-Control-Allow-Origin: *\r\n"
    "Connection: close\r\n\r\n";

  client.print(response);

  while (client.connected()) {

    camera_fb_t * fb = esp_camera_fb_get();

    if (!fb) {
      continue;
    }

    client.printf(
      "--frame\r\n"
      "Content-Type: image/jpeg\r\n"
      "Content-Length: %u\r\n\r\n",
      fb->len
    );

    client.write(fb->buf, fb->len);

    client.print("\r\n");

    esp_camera_fb_return(fb);

    delay(30);
  }

  client.stop();
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