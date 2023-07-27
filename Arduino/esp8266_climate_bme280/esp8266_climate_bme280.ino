/***************************************************************************
  This is a library for the BMP280 humidity, temperature & pressure sensor

  Designed specifically to work with the Adafruit BMP280 Breakout
  ----> http://www.adafruit.com/products/2651

  These sensors use I2C or SPI to communicate, 2 or 4 pins are required
  to interface.

  Adafruit invests time and resources providing this open source code,
  please support Adafruit andopen-source hardware by purchasing products
  from Adafruit!

  Written by Limor Fried & Kevin Townsend for Adafruit Industries.
  BSD license, all text above must be included in any redistribution
 ***************************************************************************/

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_BME280.h>
#include "mqtt_wrapper.h"

#include <cstdio>

ADC_MODE(ADC_VCC);

const int sda_pin = 4;
const int scl_pin = 5;
TwoWire MyWire;

Adafruit_BME280 bme; // I2C

const uint64_t MINUTE = 60*1000*1000;

void publishOne() {
  char Msg[64];

  snprintf(Msg, 64, "{\"temp\": %.1f, \"bat\": %.2f, \"press\": %.0f, \"hum\": %.0f}",
    bme.readTemperature(),
    (float)ESP.getVcc()/687.2,    //measure and match
    bme.readPressure(),
    bme.readHumidity()
  );  
  mqtt_publish(Msg);
}


void setup() {
  Serial.begin(115200);
  while ( !Serial ) delay(100);   // wait for native usb
  Serial.println(F("BME280 test"));
  unsigned status;
  MyWire.begin(sda_pin, scl_pin);
  status = bme.begin(0x76, &MyWire);  
  if (!status) {
    Serial.println(F("Could not find a valid BME280 sensor, check wiring or "
                      "try a different address!"));
            Serial.print("SensorID was: 0x"); Serial.println(bme.sensorID(),16);
    while (1) delay(10);
  }
  delay(10);
  mqtt_begin();

  publishOne();

  //bme.reset();

  mqtt_disconnect();

  Serial.println("Esp8266 going to sleep ...");
  ESP.deepSleep(5*MINUTE);
  delay(1000);
  while (1);  
}

void loop() {

}
