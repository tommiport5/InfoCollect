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
#include <Adafruit_BMP280.h>
#include "mqtt_wrapper.h"

#include <sstream>

const int sda_pin = 4;
const int scl_pin = 5;

TwoWire MyWire;
Adafruit_BMP280 bmp(&MyWire); // I2C

const uint64_t MINUTE = 60*1000*1000;

void publishOne() {
  std::ostringstream Msg;

  Msg << "{\"temp\": " << bmp.readTemperature();
  Msg << ", \"bat\": " << 3.*float(analogRead(A0))/870.;
  Msg << ", \"press\": " << bmp.readPressure();
  Msg << "}";

  mqtt_publish(Msg.str().c_str());
}


void setup() {
  Serial.begin(115200);
  while ( !Serial ) delay(100);   // wait for native usb
  Serial.println(F("BMP280 test"));
  unsigned status;
  //status = bmp.begin(BMP280_ADDRESS_ALT, BMP280_CHIPID);
  MyWire.begin(sda_pin, scl_pin);
  status = bmp.begin(0x76);
  if (!status) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring or "
                      "try a different address!"));
    while (1) delay(10);
  }
  delay(10);
  /* Default settings from datasheet. */
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                  Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                  Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                  Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                  Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */
  mqtt_begin();

  publishOne();

  bmp.reset();

  mqtt_disconnect();

  Serial.println("Esp8266 going to sleep ...");
  ESP.deepSleep(5*MINUTE);
  delay(1000);
  while (1);  
}

void loop() {

}
