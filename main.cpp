//-----------------------------------------------
#include "BluetoothSerial.h"
#include <Adafruit_BMP085.h>
#include <SoftwareSerial.h> 
#include <PubSubClient.h>  
#include <ArduinoJson.h>
#include <Preferences.h>
#include <Arduino.h>
#include <string>
#include "MHZ19.h"
#include <Wire.h>
#include <WiFi.h>
#include "time.h"  
#include <SPI.h>
#include <Esp.h>
#include "DHT.h"
//-----------------------------------------------
//standard interval between sensor read 
int standard_interval = 500;
//count of read
//final delay is standard_interval * iter_count
int iter_count = 10;
//-----------------------------------------------
//wi-fi connection data
char ssid[] = "otsASUS";    
char pass[] = "19216811";
//-----------------------------------------------
//mqtt connection data
#define MQTT_HOST "trk6k0.messaging.internetofthings.ibmcloud.com"
#define MQTT_PORT 1883
#define MQTT_DEVICEID "d:trk6k0:esp:esp_32" 
#define MQTT_USER "use-token-auth"
#define MQTT_TOKEN "c*2qQCJa*NqD+GASsH"
#define MQTT_TOPIC "iot-2/evt/status/fmt/json"
#define MQTT_TOPIC_DISPLAY "iot-2/cmd/change_relay/fmt/json"
//-----------------------------------------------
//dht22 define
#define DHTPIN 4
#define DHTTYPE DHT22  
//mhz19b define
#define RX_PIN 19                                          
#define TX_PIN 18
//relay define
#define Relay_1 12
#define Relay_2 14
#define Relay_3 26
#define Relay_4 25
#define Relay_5 33
#define Relay_6 32
//-----------------------------------------------
//preferences for saving relay state
Preferences preferences;
//sensor objects                                        
MHZ19 _mhz19b;
Adafruit_BMP085 bmp;
DHT dht(DHTPIN, DHTTYPE);
//serial for mhz19b                             
SoftwareSerial mhz19b_Serial(RX_PIN, TX_PIN);
//bluetooth object
BluetoothSerial SerialBT;  
//-----------------------------------------------
//sensor variables
float temperature = 0;
float pressure = 0;
float co2 = 0;
float humidity = 0;
//-----------------------------------------------
//mqtt objects
void callback(char* topic, byte* payload, unsigned int length);
WiFiClient wifiClient;
PubSubClient mqtt(MQTT_HOST, MQTT_PORT, callback, wifiClient);
//-----------------------------------------------
//json objects
StaticJsonDocument<300> jsonDoc;
JsonObject payload = jsonDoc.to<JsonObject>();
JsonObject status = payload.createNestedObject("data"); 
static char msg[200];
//-----------------------------------------------
//time variables
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 7200;
const int daylightOffset_sec = 3600;
//-----------------------------------------------
//function: relay control (on/off)
void relay_control(int r_number, int r_state)
{
  if (r_state == 2)
    return;
  if (r_number == 1)
    digitalWrite(Relay_1, r_state);
  if (r_number == 2)
    digitalWrite(Relay_2, r_state);
  if (r_number == 3)
    digitalWrite(Relay_3, r_state);
  if (r_number == 4)
    digitalWrite(Relay_4, r_state);
  if (r_number == 5)
    digitalWrite(Relay_5, r_state);
  if (r_number == 6)
    digitalWrite(Relay_6, r_state);
}
//-----------------------------------------------
//function: get time from pool.ntp.org
unsigned long getTime() {
  time_t now;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return(0);
  }
  time(&now);
  return now;
}
//-----------------------------------------------
//function: get new messages from mqtt
void callback(char* topic, byte* payload, unsigned int length) 
{
  Serial.println("Message arrived: ");
  payload[length] = 0;
  //print message
  Serial.println((char *)payload);
  //parse json
  StaticJsonDocument<200> doc;
  deserializeJson(doc, payload);
  int r_number = doc["r_n"];
  int r_state = doc["r_s"];
  //change relay state and save it
  String relay = "r" + String(r_number);
  relay = relay + "_s";
  preferences.begin("relay_state", false);
  preferences.putUInt(relay.c_str(), r_state);
  preferences.end();
  relay_control(r_number, r_state);
}
//-----------------------------------------------
//function: read data from sensors
void read_modules()
{
  int iter = 0;
  float dht_temp = 0;
  float bmp_pres = 0;
  float mhz19_co2 = 0;
  float dht_humi = 0;
  while (iter < iter_count) {
    //bmp180 data
    dht_temp += dht.readTemperature();
    bmp_pres += bmp.readPressure();
    //mhz19b data
    mhz19_co2 += _mhz19b.getCO2();
    //DHT22 data
    dht_humi += dht.readHumidity();
    iter++;
    //check messages from mqtt
    mqtt.loop();
    delay(standard_interval);
  }
  //count average value
  temperature = dht_temp/iter_count;
  pressure = bmp_pres/iter_count;
  co2 = mhz19_co2/iter_count;
  humidity = dht_humi/iter_count;
}
//-----------------------------------------------
//function: setup
void setup()
{
  //start bluetooth
  SerialBT.begin("ESP32");
  //relay output
  pinMode(Relay_1, OUTPUT); 
  pinMode(Relay_2, OUTPUT);
  pinMode(Relay_3, OUTPUT);
  pinMode(Relay_4, OUTPUT);
  pinMode(Relay_5, OUTPUT);
  pinMode(Relay_6, OUTPUT);
  //read preferences
  preferences.begin("relay_state", false);
  unsigned int r1_s = preferences.getUInt("r1_s", 2);
  unsigned int r2_s = preferences.getUInt("r2_s", 2);
  unsigned int r3_s = preferences.getUInt("r3_s", 2);
  unsigned int r4_s = preferences.getUInt("r4_s", 2);
  unsigned int r5_s = preferences.getUInt("r5_s", 2);
  unsigned int r6_s = preferences.getUInt("r6_s", 2);
  //switch relay (last state from memory)
  relay_control(1, r1_s);
  relay_control(2, r2_s);
  relay_control(3, r3_s);
  relay_control(4, r4_s);
  relay_control(5, r5_s);
  relay_control(6, r6_s);
  preferences.end();
  //serial for debugging (maybe)
  Serial.begin(115200);
  //serial for mhz19b    
  mhz19b_Serial.begin(9600);
  //sensor's init   
  _mhz19b.begin(mhz19b_Serial); 
  _mhz19b.autoCalibration(); 
  bmp.begin();
  dht.begin();
  //wi-fi connect
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Error. WiFi is not available! Wait 5 sec...");
    delay(5000);
  }
  Serial.println("WiFi Connected.");
  //mqtt ibm cloud connect
  while (true) 
  {
    if (mqtt.connect(MQTT_DEVICEID, MQTT_USER, MQTT_TOKEN)) {
      Serial.println("IBM Cloud OK. MQTT Connected.");
      mqtt.subscribe(MQTT_TOPIC_DISPLAY);
      break;
    } else {
      Serial.println("Error. MQTT Failed to connect! Wait 5 secs...");
      delay(5000);
    }
  }
  //time configuration
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
}
//-----------------------------------------------
//function: loop
void loop()
{
  //check messages from mqtt
  mqtt.loop();
  //if mqtt not connected
  while (!mqtt.connected()) {
    Serial.println("Attempting MQTT connection...");
    if (mqtt.connect(MQTT_DEVICEID, MQTT_USER, MQTT_TOKEN)) {
      Serial.println("MQTT Connected.");
      mqtt.subscribe(MQTT_TOPIC_DISPLAY);
      mqtt.loop();
    } else {
      Serial.println("Error. MQTT Failed to connect!");
      delay(5000);
    }
  }
  //read data from sensors
  read_modules();
  //build json
  int time = getTime();
  status["time"] = time;
  status["tem"] = temperature;
  status["pre"] = pressure;
  status["co2"] = co2;
  status["hum"] = humidity;
  serializeJson(jsonDoc, msg, 200);
  Serial.println("Sending ok, message: ");
  Serial.print(msg);
  //send to mqtt ibm cloud
  if (!mqtt.publish(MQTT_TOPIC, msg)) 
  {
    Serial.println("Error. MQTT Publish failed!");
  }
}
//-----------------------------------------------