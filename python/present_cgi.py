#!/usr/bin/python3
'''
Created on 16.12.2018
collect is the cgi-script that delivers the daemons data to the web server
@author: Dad
'''
import socket
import cgi
import cgitb
import logging

# this also works, if the module is started without the PYTHONPATH set
import sys
import pathlib as p
import importlib

pp = p.Path(sys.argv[0])
pack = pp.resolve().parent
common = importlib.import_module('__init__', package=str(pack))

#Sel = selectors.DefaultSelector()

FORMAT = '%(asctime)-15s present_cgi: %(message)s'
logging.basicConfig(filename=common.ComPath+common.App+'.log', format=FORMAT)
Log = logging.getLogger(common.App)
Log.setLevel(logging.INFO)

def other():
#     Answer = "["
#     for da in DatArr:
#         Answer += str(da) + ","
#     Answer = Answer.rstrip(",") + "]"
    pass
    

if __name__ == '__main__':
    cgitb.enable(display=0, logdir=common.ComPath)
    pars = cgi.FieldStorage()
    if not 'drq' in pars:
        drq ='d'
    else:
        drq = str(pars.getvalue('drq'))
    Log.debug('cgi invoked with par ' + drq)
    print('Access-Control-Allow-Origin: *')
    print('Content-Type: application/json')
    print('Cache-Control: no-cache')
    sock = socket.socket()
    if drq in "TPHb":
        sock.connect(common.Socket2)
    else:
        sock.connect(common.LOCAL_ADDR)
    try:
        num = sock.send(bytes(drq,'UTF-8'))
        lng = sock.recv(8)
        # print(str(lng,"utf-8"))
        l = int(str(lng,"utf-8")[1:7])
        # print header
        print('Content-Length: {}'.format(l))
        print('')
        togo = l
        while togo > 0:
            chunk = min(togo, 4096)
            s = str(sock.recv(chunk),'utf-8')
            print(s, end='')
            togo -= len(s)
        print('')
    except ValueError:
        print("Err: did not receive length info")
    finally:
        sock.shutdown(1)
        sock.close()
