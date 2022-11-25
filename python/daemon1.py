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

from InfoCollect import LOCAL_ADDR, ComPath, App, File, Version
from InfoCollect import djson
from config import Config
from multiprocessing import Lock, Condition
from InfoCollect import mutex as Mutex

import logging
import os.path
import traceback

# App = __package__
RootTopic = "Esp32/807D3AFDE135/climate/"
ResourceTopic = "Esp32/807D3AFDE134/resource/"

Last = {'G':""}
Text = {'G':"VOL", 'D':'VOL', 'F':'DTL', 'X':'AVG'}

EchoOccured = Condition()
FORMAT = '%(asctime)-15s daemon1: %(message)s'
logfile = ComPath+App+'.log'
logging.basicConfig(filename=logfile, format=FORMAT)
Log = logging.getLogger(App)
Log.setLevel(logging.INFO)

def connectMQTT(mqttc):
    # mqttc.message_callback_add(RootTopic + "moisture", on_moisture)    
    # mqttc.message_callback_add(RootTopic + "light", on_light)    
    mqttc.message_callback_add(RootTopic + "echo", on_echo)
    mqttc.message_callback_add(ResourceTopic + "gas/null/json", on_gas)
    mqttc.on_message = on_message
    mqttc.on_disconnect = onDisConnect
    mqttc.on_connect = onConnect
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
    # su = mqttc.subscribe([(RootTopic + "#", 0), (ResourceTopic + "gas/null/json",0)])
    su = mqttc.subscribe((ResourceTopic + "gas/null/json",0))
    Log.info("MQTT client connected with result {} and subscribed with id {}".format(rc, su[1]))

def subTopic(complete):
    return complete.rsplit('/',maxsplit=1)[1]

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
        
# resorting is much simpler than for daemon2, because there is only one sender
# simply add the 'cols' object and reformat the 'rows'
def resort(valarr, txt):
    st = {'cols': [["datetime", "DAT"], ["number", txt]], 'rows': []}
    for v in valarr:
        st['rows'].append([str(v[0]), v[1]])
    return st

def sendAnswer(conn, req):
    if req in 'G':
        mut = Mutex[req]
        fpath = ComPath + File[req] + ".json"
    elif req in 'DFX':
        mut = Mutex[req]
        fpath = ComPath + File[req] + ".daily.json"
    else:
        Log.error("Illegal request {}".format(req))
        return
    Trans = []
    try:
        mut.acquire()
        Log.debug('Trying to read ' + fpath)
        with open(fpath) as DatFile:
            Trans = json.load(DatFile, object_hook=djson.datetime_decoder)
    except OSError:
        Log.warn("Sending empty " + fpath)
    mut.release()
    Sorted = json.dumps(resort(Trans, Text[req]), cls=djson.DateTimeJSONEncoder)
    # print(Sorted)
    lng = len(Sorted)
    try:
        conn.sendall(bytes("L{:06d};".format(lng),"UTF-8"))
        conn.sendall(bytes(Sorted,"UTF-8"))
    except BaseException as e:
        Log.error("Could not send answer: %s", str(e))


def on_message(_client, _userdata, message):
    Log.info("Received unknown message - topic: {}, payload: {}".format(message.topic, str(message.payload, encoding='utf-8')))
    
def storeContent(req, select_func, supply_func, message):
    fpath = ComPath + File[req] + ".json"
    try:
        now = datetime.now()
        cur = json.loads(str(message.payload, encoding='utf-8'))
        if not cur or not select_func(cur):
            Log.warning("Suppressed empty value for {}".format(req))
            return
        DatArr = []
        try:
            with open(fpath) as DatFile:
                DatArr = json.load(DatFile, object_hook=djson.datetime_decoder)
            for _ in range(len(DatArr)):
                if now - DatArr[0][0] > timedelta(days=1): 
                    DatArr.pop(0) 
                else:
                    break
        except OSError:
            Log.info('Started with new ' + fpath)
            if not select_func(cur):
                Log.debug('No content "{}" received'.format(req)) 
                return
        if Last[req] == select_func(cur) and len(DatArr)>2 :
            Log.debug('Same {} ({}) supressed'.format(req, Last[req])) 
            return
        Last[req] = select_func(cur)
        DatArr.append(supply_func(cur))
        Mutex[req].acquire()
        try:
            with open(fpath,'w') as DatFile:
                json.dump(DatArr, DatFile, cls=djson.DateTimeJSONEncoder)
                Log.debug(fpath + " written")
        except Exception as e:
            Log.error(str(e))
        finally:
            Mutex[req].release()
            Log.debug('message handled')
    except Exception as e:
        Log.error("Exception {}: {}".format(type(e), str(e)))
    
def on_light(_client, _userdata, message):
    storeContent('A', lambda cur: cur['ambient'], lambda cur: [datetime.now(), cur['ambient']], message)
    
LastRaw = ""

def on_gas(_client, _userdata, message):
    global LastRaw
    data = json.loads(str(message.payload, encoding='utf-8'))
    if data['error'] != 'no error':
        if data['raw'] != LastRaw:
            LastRaw = data['raw']
            Log.warning('Gasmeter error: ' + data['error'])
    else:
        if LastRaw != "":
            Log.warning('Gasmeter ok, raw: ' + data['raw'])
            LastRaw = ""
        storeContent('G', lambda cur: cur['value'], lambda cur: [datetime.now(), cur['value']], message)

def on_moisture(_client, _userdata, message):
    storeContent('M', lambda cur: cur['moisture'], lambda cur: [datetime.now(), cur['moisture']], message)
    
def lookupAussen():
    for sender in Config.items():
        if "Aussen" in sender[1]["name"]:
            return sender[0]
    return None
    
def averageForToday(act_dat):
    Aussen = lookupAussen()
    if not Aussen: return None
    sum = 0
    count = 0
    for point in act_dat:
        if point["sender"] == Aussen:
            sum += point["val"]
            count += 1
    if count == 0: return None
    else: return [date.today(), sum / count]

def deltaForToday(act_dat):
        last = act_dat[-1]
        for entries in act_dat:
            if entries[0].date() == last[0].date():
                return [last[0].date(), last[1] - entries[1]]
        
def lastForToday(act_dat):
        last = act_dat[-1]
        return [last[0].date(), last[1]]
        
def calculateDaily(src, dst, newValFunc, requireDate=True):
    Mutex[src].acquire()
    if not os.path.exists(ComPath + File[src] + ".json"):
       Log.warning("No source file {}.json".format(File[src]))
       Mutex[src].release()
       return
    try:
        with open(ComPath + File[src] + ".json") as ga:
            act_dat = json.load(ga, object_hook=djson.datetime_decoder)
    except Exception:
       Log.warning("Cannot read source file in calculateDaily")
       Mutex[src].release()
       return
    try:
        Mutex[src].release()
        last = act_dat[-1]
        if requireDate and (not last or last[0].date() != date.today()):
            Log.warning("No values for {} in {}.json".format(str(date.today())), File[src])
            return
        cont = []
        Mutex[dst].acquire()
        if os.path.exists(ComPath + File[dst] + ".daily.json"):
            with open(ComPath + File[dst] + ".daily.json") as gdr:
                cont = json.load(gdr, object_hook=djson.datetime_decoder)
        cont.append(newValFunc(act_dat))
        # print(cont)
        with open(ComPath + File[dst] + ".daily.json","w") as gdw:
            json.dump(cont, gdw, cls=djson.DateTimeJSONEncoder)
    except Exception as e:
        with open(logfile, "a") as lg:
            traceback.print_exc(file=lg)
    finally:
        Mutex[dst].release()
        
if __name__ == '__main__':
    if len(sys.argv) > 1 and (sys.argv[1] == "-v" or sys.argv[1] == "--version"):
        print(Version)
        sys.exit(0)
    # create a thread that subscribes to the mqtt messages
    Log.info("daemon1 version {} started".format(Version))
    mqttc = mqtt.Client()
    connectMQTT(mqttc)
    Finished = False
    #create a socket and wait for triggers from the web interface    
    sock = socket.socket()
    sock.bind(LOCAL_ADDR)
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
                    Log.debug("received: >{}<".format(tg.decode()))
                    if req in "GDFX":
                        Log.debug('processing request ' + req)
                        sendAnswer(conn, req)
                    elif req == 'q':
                        Processing = False
                        Finished = True
                        Log.info('server shutdown')
                    elif req == 's':
                        Log.debug('sendig status')
                        sendStatus(conn, mqttc)
                    elif req == 'r':
                        Log.debug('reconnecting')
                        mqttc.loop_stop()
                        mqttc = mqtt.Client()
                        connectMQTT(mqttc)
                    elif req == 'd':
                        calculateDaily('G', 'D', deltaForToday)
                        calculateDaily('G', 'F', lastForToday)
                        calculateDaily('T', 'X', averageForToday, False)
                else:
                    Log.debug("Fake receive")
                    Processing = False
        # Sel.unregister(sock)
