## InfoCollect
InfoCollect provides an environment for collecting and visualising climate and resource consumption data of your home. 

It is based on the project [AI-on the edge-device](https://github.com/jomjol/AI-on-the-edge-device) by @jomjol which also appeared in Make magazine 4 / 2021.
Originally conceived as a device to read out a watermeter, it has been adapted to many read out purposes by a growing comunity. 

My adaption is for a standard German gas meter, and the softwate serves this out of the box. I only had to provide a mechanical stand and a cardboard "housing" to eliminate ambient light and reduce reflections.
![cardboard housing](/assets/20221119_165635.jpg)

### What is InfoCollect?
InfoCollect is a software framework in Python, designed to run on a Raspberry Pi together with a MQTT broker and a web server. It collects and persists data from the gasmeter, and visualises them with the Goohle 
Visualisation API. It can be supplemented by simple battery operated sensors with an ESP8266 microcontroller that can gather climate data. Also provided is the HTML and javascript code as example
for the presentation. Here are some screenshots from this sample implementation:
![gas consumation daily](/assets/gas_daily.png)
![gas and temperature combined](/assets/gas_temp.png)

![temperature](/assets/temp.png)
![humidity](/assets/humidity.png)
![pressure](/assets/pressure.png)

### Requirements
Apart from the camera and controller from the [AI-on the edge-device](https://github.com/jomjol/AI-on-the-edge-device) project, you need:
- A Raspberry Pi
	
	I use a Raspi 2 B with raspbian buster, that's way enough. It comes with python 3.7 which is ok too.
- A Webserver on this machine
	
	I use lighttpd. nginx should do as well, Apache could be too big for the raspi.
- A MQTT Broker
	
	I use mosquitto [https://mosquitto.org/](https://mosquitto.org/)
- paho-mqtt 1.6, a mqtt client library for python

If you want to gather the climate data, you can use an ESP8266 module which is wired like this: [sensor_module schematic](/assets/sensor_module.pdf)

To the connector labelled BMP280 you can connect any of the various BME280, BMP280 or SHT21 sensor modules via I2C Bus. The provide temperature, humidity or atmosphreric pressure in
various combinations. The corresponding Arduino code can be found in the Arduino directory. This hardware can be powered by two AA (Mignon) AlMn  batteries for several months, because
it usually is in deep sleep and awakes only every 5 minutes to send one set of values via WLAN.

I use an ESP8266-12F, but thats a bit tricky because of the unusual grid of the I/O pads.

### Installation
1. Build the [AI-on the edge-device](https://github.com/jomjol/AI-on-the-edge-device) project up to the point that you can see your agasmeter in yout browser and verify
the reading.
2. Install the MQTT broker and web browser on the Raspi. Add your raspi user to the group www-data.
3. Make sure that your raspi user is in the sudoers group. Download and execute the [install.sh](/assets/install.sh) on the raspi. 

Now you can start the InfoCollect processes with
```
sudo systemctl start infocollect
```

### Comming up
#### Analyze the correlation between outside temperature and gas consumation
I will use pandas and scikit-learn for that
#### Prepare an installation script
#### Integrate the electricity meter
I got some ideas for that from [this video](https://www.youtube.com/watch?v=l99ZXvqqBRY&list=FLW6Zg6QSCuyhSc68cUOKlCA&index=1&t=1115s)



