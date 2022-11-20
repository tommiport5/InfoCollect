/**
 * mqtt_wrapper
 * mqtt and wifi handling
 */

#ifndef _MQTT_WRAPPER
#define _MQTT_WRAPPER

bool mqtt_reconnect();
void mqtt_begin();
bool mqtt_skip();
void mqtt_publish(const char *);
void mqtt_disconnect();

#endif
