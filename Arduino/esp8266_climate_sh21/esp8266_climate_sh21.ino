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
#include <SHT21.h>
#include "mqtt_wrapper.h"

#include <sstream>

const int sda_pin = 4;
const int scl_pin = 5;

SHT21 bmp; // I2C

const uint64_t MINUTE = 60*1000*1000;

void publishOne() {
  std::ostringstream Msg;

  Msg << "{\"temp\": " << bmp.getTemperature();
  Msg << ", \"bat\": " << 3.*float(analogRead(A0))/870.;
  Msg << ", \"hum\": " << bmp.getHumidity();
  Msg << "}";

  mqtt_publish(Msg.str().c_str());
  //Serial.println(Msg.str().c_str());
}


void setup() {
  Serial.begin(115200);
  while ( !Serial ) delay(100);   // wait for native usb
  Serial.println(F("SHT21test"));
  unsigned status;
  //status = bmp.begin(BMP280_ADDRESS_ALT, BMP280_CHIPID);
  Wire.begin(sda_pin, scl_pin);
  delay(10);
  /* Default settings from datasheet. */
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
