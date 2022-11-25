#!/usr/bin/python3
'''
Created on 15.12.2018
The daemon subscribes to the MQTT broker
daemon is the persistent version, there is also a daemon_volatile version 
without file storage

!! directory /var/lib/misc must exist !!
 
@author: Dad
'''
import paho.mqtt.client as mqtt
import json
from datetime import datetime, timedelta, date
import select
import socket
import sys

from InfoCollect import Socket2, ComPath, App, File, Version
from InfoCollect import djson
from InfoCollect import mutex as Mutex
from multiprocessing import Lock, Condition

import logging
import os.path
import traceback

RootTopic = "Esp32/807D3AFDE135/climate/"
AggregatorTopic = "Esp32/aggregat/"

EchoOccured = Condition()
FORMAT = '%(asctime)-15s daemon2: %(message)s'
logfile = ComPath+App+'.log'
logging.basicConfig(filename=logfile, format=FORMAT)
Log = logging.getLogger(App)
Log.setLevel(logging.INFO)

def connectMQTT(mqttc):
    Log.debug("daemon2 connecting ...")
    mqttc.message_callback_add(AggregatorTopic + "temp", on_temp)
    mqttc.message_callback_add(AggregatorTopic + "hum", on_hum)    
    # mqttc.message_callback_add(RootTopic + "light", on_light)    
    mqttc.message_callback_add(AggregatorTopic + "press", on_press)
    mqttc.message_callback_add(AggregatorTopic + "bat", on_bat)
    mqttc.on_message = on_message
    mqttc.on_disconnect = onDisConnect
    mqttc.on_connect = onConnect
    mqttc.on_subscribe = onSubscribe
    mqttc.connect("localhost")
    mqttc.loop_start()
    
def on_echo(_client, _userdata, _message):
    EchoOccured.acquire()
    EchoOccured.notify()
    EchoOccured.release()
    
def onDisConnect(client, _userdata, rc):
    if rc != 0:
        Log.error("MQTT client disconnected with error {}".format(rc))
        sock = socket.socket()
        sock.connect(LOCAL_ADDR)
        sock.send(bytes("r",'UTF-8'))   # reconnect
        sock.shutdown(1)
        sock.close()
    else:
        Log.info("MQTT client disconnected without error")

def onConnect(_client, _userdata, _flags, rc):
    Log.debug("daemon2 subscribing ...")
    su = mqttc.subscribe((AggregatorTopic + "#", 0))
    Log.info("daemon2 connected with result {} and subscribed with id {}".format(rc, su[1]))

def onSubscribe(client, _userdata, mid, _granted_qos):
    Log.info("subscription with id {} has been granted".format(mid))
    

def sendStatus(conn, mqttc):
    try:
        if (mqttc.is_connected()):
            Ret = "Connected"
            EchoOccured.acquire()
            mqttc.publish(RootTopic + "echo")
            Answered = EchoOccured.wait(10)
            EchoOccured.release()
            Ret += " and responding" if Answered else " but not responding"
        else:
            Ret = "Not connected"
        lng = len(Ret)
        conn.sendall(bytes("L{:06d};".format(lng),"UTF-8"))
        conn.sendall(bytes(Ret,"UTF-8"))
    except BaseException as e:
        Log.error("Could not send status: %s", str(e))
        
# sort the valarray from an array of filtered mqtt messages
# [{"dt": nested_datetime}, "sender":"876", val: 19.9}, ...]
# to an object suitable for a gviz line chart
# {cols: ["datetime": "dt", number: name_1, ..., number: name_n],
#  rows: [[nested_datetime, , ,20.5,  ...],
#         [nested_datetime, ,17.2 ,,  ...
#        ]
# }
def resort(valarr):
    colnames = []
    # The LineChart connects points based on adjacency in the DataTable, not adjacency in value
    # (from stackoverflow)
    sva = sorted(valarr, key=lambda uva: uva['sender'])
    for v in sva:
        if not v["sender"] in colnames:
            colnames.append(v["sender"])
    if len(colnames) == 0: return
    svals = {'cols': [["datetime", "TME"]], 'rows': []}
    for n in colnames:
        svals['cols'].append(["number", n])
    for v in sva:
        cols = [None for i in range(len(colnames))]
        cols[colnames.index(v["sender"])] = v['val']
        svals['rows'].append([str(v["dt"])] + cols)
    return svals
    
LastAgg = {'temp': {}, 'press': {}, 'hum': {}}
LastSingle = {'bat': {}}
    
def sendAnswer(conn, req):
    if req in 'TPH':
        mut = Mutex[req]
        fpath = ComPath + File[req] + ".json"
    else:
        Log.error("Illegal request {}".format(req))
        return
    Sorted = {}
    try:
        mut.acquire()
        Log.debug('Trying to read ' + fpath)
        with open(fpath) as DatFile:
            Answer = json.load(DatFile, object_hook=djson.datetime_decoder)
    except OSError:
        Log.warn("Sending empty " + fpath)
    mut.release()
    Sorted = json.dumps(resort(Answer), cls=djson.DateTimeJSONEncoder)
    lng = len(Sorted)
    try:
        conn.sendall(bytes("L{:06d};".format(lng),"UTF-8"))
        conn.sendall(bytes(Sorted,"UTF-8"))
    except BaseException as e:
        Log.error("Could not send answer: %s", str(e))
        
def sendSingle(conn, req):
    Log.debug("Sending single >{}<".format(req))
    if req in 'b':
        mut = Mutex[req]
    else:
        Log.error("Illegal request {}".format(req))
        return
    Answer = None
    mut.acquire()
    Answer = json.dumps(LastSingle['bat'], cls=djson.DateTimeJSONEncoder)
    mut.release()
    lng = len(Answer)
    try:
        conn.sendall(bytes("L{:06d};".format(lng),"UTF-8"))
        conn.sendall(bytes(Answer,"UTF-8"))
    except BaseException as e:
        Log.error("daemon2 could not send answer: %s", str(e))


def on_message(_client, _userdata, message):
    Log.info("Received unknown message - topic: {}, payload: {}".format(message.topic, str(message.payload, encoding='utf-8')))
    
def on_light(_client, _userdata, message):
    storeContent('A', lambda cur: cur['ambient'], lambda cur: [datetime.now(), cur['ambient']], message)
    
def storeAgg(req, valdict):
    Mutex[req].acquire()
    fpath = ComPath + File[req] + ".json"
    valarr = []
    try:
        with open(fpath) as fi:
            valarr= json.load(fi, object_hook=djson.datetime_decoder)
            for _ in range(len(valarr)):
                if datetime.now() - valarr[0]['dt'] > timedelta(days=1): 
                    valarr.pop(0) 
                else:
                    break
    except FileNotFoundError:
        pass
    try:
        valarr.append(valdict)
        with open(fpath, "w") as fi:
            json.dump(valarr, fi, cls=djson.DateTimeJSONEncoder)
            Log.debug("Successfully wrote {}".format(fpath))
    except BaseException as e:
        Log.debug("Exception %s writing %s", str(e), fpath)
    finally:
         Mutex[req].release()

def storeContent(req, message):
    item = File[req]
    data = json.loads(str(message.payload, encoding='utf-8'))
    if data['sender'] in LastAgg[item] and LastAgg[item][data['sender']] == data['val']:
        return
    LastAgg[item][data['sender']] = data['val']
    storeAgg(req, data)

# tasks:
# filter out same data and persist one row for the data
def on_temp(_client, _userdata, message):
    Log.debug("Received '{}'".format(str(message.payload)))
    storeContent('T', message)

def on_bat(_client, _userdata, message):
    data = json.loads(str(message.payload, encoding='utf-8'))
    Log.debug("Received '{}'".format(str(message.payload)))
    Mutex['b'].acquire()
    LastSingle['bat'][data['sender']] = {"dt": data['dt'], "val": data['val']}
    Mutex['b'].release()
    
def on_hum(_client, _userdata, message):
    Log.debug("Received '{}'".format(str(message.payload)))
    storeContent('H', message)

def on_press(_client, _userdata, message):
    Log.debug("Received '{}'".format(str(message.payload)))
    storeContent('P', message)
        
if __name__ == '__main__':
    if len(sys.argv) > 1 and (sys.argv[1] == "-v" or sys.argv[1] == "--version"):
        print(Version)
        sys.exit(0)
    # start the aggregator as a separate process
    # os.system("python3 aggregator.py") better have all the subprocesses started by daemon.py
    # create a thread that subscribes to the mqtt messages
    Log.info("daemon2 version {} started".format(Version))
    mqttc = mqtt.Client()
    connectMQTT(mqttc)
    Finished = False
    #create a socket and wait for triggers from the web interface    
    sock = socket.socket()
    sock.bind(Socket2)
    sock.setblocking(True)
    sock.listen(10)
    while not Finished:
        r,w,x = select.select([sock], [], [sock])
        if sock in x:
            Log.info("Exceptional condition")
            continue
        if sock in r:
            conn, addr = sock.accept()
            Processing = True
            Log.debug('received socket request')
            while Processing:
                tg = conn.recv(1)
                if tg:
                    req  = tg.decode()
                    Log.debug("received: >{}< from socket".format(tg.decode()))
                    if req in r'TPH':
                        Log.debug('processing request ' + req)
                        sendAnswer(conn, req)
                    elif req in r'b':
                        sendSingle(conn, req)
                    elif req == 'q':
                        Processing = False
                        Finished = True
                        Log.info('server shutdown')
                    elif req == 's':
                        Log.debug('sendig status')
                        sendStatus(conn, mqttc)
                else:
                    Log.debug("Fake receive on daemon2")
                    Processing = False
    # mttc.publish("Esp32/aggregator/cmd", '123')
