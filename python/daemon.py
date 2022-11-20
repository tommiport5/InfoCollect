#!/usr/bin/python3
'''
Manages all the apps for InfoCollect
Is intentet to be started and stopped as service 
@author: Dad
'''
import subprocess
import sys
import json
from pathlib import Path
import signal
from threading import Condition
import socket
from InfoCollect import LOCAL_ADDR, Socket2, ComPath, App
import logging
import os.path

FORMAT = '%(asctime)-15s daemon: %(message)s'

logfile = ComPath+App+'.log'
logging.basicConfig(filename=logfile, format=FORMAT)
Log = logging.getLogger(App)
Log.setLevel(logging.INFO)

d1sock = socket.socket()
d2sock = socket.socket()
aggregator = None

term = Condition()

def KillCatcher(signum, frame):
    Log.debug("daemon received signal, stopping subprocesses ...")
    d1sock.connect(LOCAL_ADDR)
    d2sock.connect(Socket2)
    d1sock.send(b"q")
    d2sock.send(b"q")
    aggregator.send_signal(signal.SIGUSR1)
    term.acquire()
    term.notify()
    term.release()
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = Path.cwd()
    Log.debug("starting infocollect ...")
    daemon1 = subprocess.Popen((sys.executable, path / "daemon1.py"))
    aggregator = subprocess.Popen((sys.executable, path / "aggregator.py")) # can be terminated with SIGUSR1 or mqtt cmd
    daemon2 = subprocess.Popen((sys.executable, path / "daemon2.py"))
    signal.signal(signal.SIGTERM, KillCatcher)
    # signal.signal(signal.SIGKILL, KillCatcher)
    term.acquire()
    term.wait()
    term.release()
    Log.debug("terminating infocollect ...")
    daemon1.wait()
    daemon2.wait()
    aggregator.wait()
    

