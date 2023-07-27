/**
 * local.generic.h
 * template for the Arduino constants for this installation.
 * Enter the confidential / specific data for this installation here
 * and save the file as local.h
 */
 
#ifndef _LOCAL_H
#define _LOCAL_H

static const char * SSID = "<SSID of your WLAN>";
static const char * PASSWORD = "<PASSWORD of your WLAN>";
static const char *mqtt_server = "<hostname of your mqtt server>";
static const int mqtt_port = 1884;	// default for non secure networks is 1883
static const char *MyId = "Esp32";	// Root of your mqtt topics for this project, you may choose a different one

#endif