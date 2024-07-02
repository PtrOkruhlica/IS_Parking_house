#include <WebServer.h>
#include <Wifi.h>
#include <esp32cam.h>
#include <esp_camera.h>

define LED 4
const char* wifi = "XXXXXXXX";
const char* pass = "XXXXXXXX";

WebServer server(80);

static auto pic1 = esp32cam::Resolution::find(1600, 1200);

void photoCreate() {
  auto photo = esp32cam::capture();
  if(photo == nullptr){
    Serial.println("Žiadne dáta");
    server.send(503, "", "");
    return;
  }
  Serial.println("Photo was created");
  server.setContentLength(photo->size());
  server.send(200, "image/jpeg");
  WiFiClient wifiClient = server.client();
  photo->writeTo(wifiClient);
}

void checkResolutionture() {
  if(!esp32cam::Camera.changeResolution(pic1)) {
    Serial.println("Zlé rozlíšenie");
  }
  photoCreate();
}

void setup() {
  
  pinMode(LED, OUTPUT);
  Serial.begin(115200);
  Serial.println();
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(pic1);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);
    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "Cam set successfully" : "Cam set unsuccessfully");
  }

  sensor_t * s = esp_camera_sensor_get();
  if( s->id.PID == OV2640_PID) {
    s->set_brightness(s,0);
    s->set_contrast(s,2);
    s->set_saturation(s,2);
    s->set_raw_gma(s,0);
  } else {
    Serial.println("Wrong choosed type of camera OVxxxx_PID");
  }

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifi, pass);
  while(WiFi.status() != WL_CONNECTED) {delay(800);}
  Serial.print("IP Address: http://");
  Serial.println(WiFi.localIP());
  server.on("/picture.jpg", checkResolutionture);
  server.begin();
}

void loop() {
  digitalWrite(LED, HIGH);
  server.handleClient();
}
