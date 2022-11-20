/**
 * mqtt_wrapper implementation
 */


#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include "mqtt_wrapper.h"
#include "local.h"

// This identifies the topic for this sensor module
static const char *id = "807D3AFDE13";

static const int to_limit = 60;  // 300sec limit for WiFi connection

static unsigned long Next;
static const unsigned long SleepSeconds = 30;

WiFiClient WClient;
PubSubClient mqtt(WClient);

String LastWillTopic, AllTopic;

bool mqtt_reconnect() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(SSID,PASSWORD);
    int i = 0;
    do {
      if (++i > 50) return false;
      Serial.print(".");
      delay(500);
    } while (WiFi.status() != WL_CONNECTED);
    Serial.println(F("Server Connected"));
  }

  //mqtt.connect(MyId, LastWillTopic.c_str(), 0, true, "offline");
  mqtt.connect(MyId);
  // for deep sleep:
  for (int i=0; i<50; i++) {
    if (mqtt.connected()) break;
    mqtt.loop();    
    delay(500);
  }
    
  if(mqtt.connected()) { 
    // Serial.println(F("Connected to Broker"));
    // Change msg
    // mqtt.publish(LastWillTopic.c_str(), "online", false);
  } else {
    Serial.println(F("Could not connect Broker"));
    delay(5000);
    return false;
  }  
  
  return true;
}

void mqtt_begin() {
  int to;
  WiFi.begin(SSID,PASSWORD);
  wdt_enable(8000);
  for (to=0; to < to_limit; to++) {
    wdt_reset();
    if (WiFi.status() == WL_CONNECTED) break;
    delay(500);
  }
  if (to == to_limit) {
    Serial.println(F("Timeout connecting WiFi"));
    ESP.restart();
  } else {
    Serial.println(F("WiFi connected"));
  }

  LastWillTopic = String("Esp32/") + id + String("/climate/status");
  AllTopic = String("Esp32/") + id + String("/climate/all");
  mqtt.setServer(mqtt_server, mqtt_port);
  mqtt_reconnect();
  Next = millis() + 30000;
}

bool mqtt_skip() {
  if (!mqtt.loop()) mqtt_reconnect();
  if (millis() < Next) return true; 
  Next = millis() + SleepSeconds*1000L;
  if (!mqtt.connected()) {
    Serial.println("lost connection >>>");
    if (!mqtt_reconnect()) {
      Serial.println("reconnect failed");    
      ESP.restart();
    }
    Serial.println("recovered");
  }
  return false;
}

void mqtt_publish(const char *st) {
  mqtt.publish(AllTopic.c_str(), st);
  for (int i=0; i<50; i++) {
    mqtt.loop();    
    delay(10);
  }   
}

void mqtt_disconnect() {
  WClient.stop();   
  mqtt.disconnect();
}
