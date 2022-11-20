#!/usr/bin/python3

import socket
import json
from InfoCollect import ComPath, App, LOCAL_ADDR
import logging
       
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(filename=ComPath+App+'.log', format=FORMAT)
Log = logging.getLogger(App)
Log.setLevel(logging.INFO)
        
if __name__ == '__main__':
    # tgs = ['l', 'q']
    try:
        sock = socket.socket()
        sock.connect(LOCAL_ADDR)
        sock.send(bytes("d",'UTF-8'))
    except Exception as e:
        Log.info('Could not trigger daily aggregation: ' + str(e))
         