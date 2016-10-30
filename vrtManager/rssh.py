
import subprocess
import socket
import time
from random import choice
from webvirtmgr.settings import BUTTER_MAPPING,MAX_BUTTER_PROCESSOR_THREAD,RSSH_MAPPING
import os
import signal

def getunusedport():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('localhost',0))
    addr,port = s.getsockname()
    s.close()
    return port

def rssh(ip):
    mapping ={}
    if ip not in RSSH_MAPPING:
        port = getunusedport()
        mapping['port'] = port
        RSSH_MAPPING[ip] =mapping
        butter_process = subprocess.Popen(['butterfly.server.py','--port='+str(port),'--host=0.0.0.0','--unsecure',
                                           "--cmd=ssh "+ip+" "])
        RSSH_MAPPING[ip]['pid'] = butter_process.pid
        RSSH_MAPPING[ip]['subprocess'] = butter_process
        return port
    else:
        RSSH_MAPPING[ip]['subprocess'].kill()
        RSSH_MAPPING[ip]['subprocess'].communicate()
        del RSSH_MAPPING[ip]
        return rssh(ip)
