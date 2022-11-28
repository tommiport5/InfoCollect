#!/usr/bin/python3
'''
Created on 19.10.2022
Aggregator 
 
@author: Dad
'''
import paho.mqtt.client as paho
import json
import logging
import re
from threading import Condition
from datetime import datetime
from InfoCollect import djson, ComPath, Version
import signal
import sys

App = "aggregator"

FORMAT = '%(asctime)-15s %(message)s'
logfile = ComPath+App+'.log'
logging.basicConfig(filename=logfile, format=FORMAT)
Log = logging.getLogger(App)
Log.setLevel(logging.INFO)

InTopic = "Esp32/+/climate/"
CmdTopic = "Esp32/aggregator/cmd"
OutTopic = "Esp32/aggregat/"

ReSender = re.compile("Esp32/([^/]*)/climate")

Quit = Condition()
#Last = {}
mqtt = paho.Client()
aggregats = ["temp", "hum", "press", "bat"]

def connectMQTT():
    mqtt.message_callback_add(InTopic + "all", on_all)
    mqtt.message_callback_add(CmdTopic, on_cmd)
    mqtt.on_connect = onConnect
    mqtt.connect("localhost")
    mqtt.loop_start()
    
def onDisConnect(client, _userdata, rc):
    if rc != 0:
        Log.error("aggregator disconnected with error {}".format(rc))
    else:
        Log.info("aggregator disconnected without error")
    
    
def extractSender(topic):
    mat = ReSender.match(topic)
    if mat and mat.group(1):
        return mat.group(1)
    else:
        return "<unknown>"  # hardly possible
    
def extractContent(message, aggregat_name):
    cur = json.loads(str(message.payload, encoding='utf-8'))
    Log.debug('Testing "{}" for "{}"'.format(cur, aggregat_name))
    if not cur or not aggregat_name in cur:
        return
    # cannot be done here, because same values in different rooms would cancel one out
    #if aggregat_name in Last and Last[aggregat_name] == cur[aggregat_name]:
    #    return
    #Last[aggregat_name] = cur[aggregat_name]
    pub = {"dt": datetime.now(), "sender": extractSender(message.topic), "val": cur[aggregat_name]}
    mqtt.publish(OutTopic + aggregat_name, json.dumps(pub, cls=djson.DateTimeJSONEncoder))

def onConnect(_client, _userdata, _flags, rc):
    su = mqtt.subscribe([(InTopic + "all", 0), (CmdTopic ,0)])
    Log.info("Aggregator subscribed with result {} and mid {}".format(rc, su[1]))

def on_all(_client, _userdata, message):
    Log.debug("Received '{}'".format(str(message.payload)))
    for ag in aggregats:
        extractContent(message, ag)

def on_cmd(_client, _userdata, message):
    Log.debug("Received '{}'".format(message.payload))
    Quit.acquire()
    Quit.notify()
    Quit.release()
    
def Terminator(_signum, _frame):
    Log.debug("Received signal from starter process")
    Quit.acquire()
    Quit.notify()
    Quit.release()
    
if __name__ == '__main__':
    if len(sys.argv) > 1 and (sys.argv[1] == "-v" or sys.argv[1] == "--version"):
        print(Version)
        sys.exit(0)
    # create a thread that subscribes to the mqtt messages
    Log.info("aggregator version {} started".format(Version))
    connectMQTT()
    signal.signal(signal.SIGTERM, Terminator)  
    Quit.acquire()
    Quit.wait()
    Log.info("Aggregator quitted")

