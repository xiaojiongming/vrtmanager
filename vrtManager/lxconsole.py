import socket
import subprocess
from random import choice
import zmq
import sys,os

class butterflycontroller:
    def __init__(self,maxbutterthread=50):
        self.__maxbutterthread = maxbutterthread
        self.__buttermaper = {}
        self.__zeromqwokerport = 33456
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.REP)
        self.__socket.bind('tcp://*:%s'%self.__zeromqwokerport)
        self.cleanbutter()
        while True:
            message = self.__socket.recv_string()
            supervisorip,vmname = message.split(',')
            port = self.createbutter(supervisorip,vmname)
            self.__socket.send(str(port))

    def getunusedport(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', 0))
        addr, port = s.getsockname()
        s.close()
        return port

    def cleanbutter(self):
        cmd = 'ps -ef | grep butterfly'
        f = os.popen(cmd)
        lines = f.readlines()
        for line in lines:
            column = line.split()
            pid = column[1]
            name = column[7]
            if name.startswith('/usr/bin/python'):
                cmd = 'kill -9 %d' % int(pid)
                run = os.system(cmd)

    def createbutter(self,supervisorip,vmname):
        if vmname:
            if len(self.__buttermaper) >= self.__maxbutterthread:
                butter_name = [name for name in self.__buttermaper]
                del_butter = choice(butter_name)
                self.__buttermaper[del_butter]['subprocess'].kill()
                self.__buttermaper['subprocess'].communicate()
                del self.__buttermaper[del_butter]
            if vmname not in self.__buttermaper:
                mapping = {}
                mapping['port'] =self.getunusedport()
                self.__buttermaper[vmname] = mapping
                butter_process = subprocess.Popen(
                ['/bin/butterfly.server.py', '--host=0.0.0.0', '--port=' + str(mapping['port']), '--unsecure',
                 "--cmd=virsh -c lxc+tcp://" + supervisorip + "/ console " + vmname + ""])
                self.__buttermaper[vmname]['pid'] = butter_process.pid
                self.__buttermaper[vmname]['subprocess'] = butter_process
                return mapping['port']
            else:
                self.__buttermaper[vmname]['subprocess'].kill()
                self.__buttermaper[vmname]['subprocess'].communicate()
                del self.__buttermaper[vmname]
                return self.createbutter(supervisorip, vmname)
        else:
            if supervisorip not in self.__buttermaper:
                mapping = {}
                mapping['port'] = self.getunusedport()
                self.__buttermaper[supervisorip] = mapping
                butter_process = subprocess.Popen(
                    ['butterfly.server.py', '--port=' + str(mapping['port']), '--host=0.0.0.0', '--unsecure',
                     "--cmd=ssh " + supervisorip + " "])
                self.__buttermaper[supervisorip]['pid'] = butter_process.pid
                self.__buttermaper[supervisorip]['subprocess'] = butter_process
                return mapping['port']
            else:
                self.__buttermaper[supervisorip]['subprocess'].kill()
                self.__buttermaper[supervisorip]['subprocess'].communicate()
                del self.__buttermaper[supervisorip]
                return self.createbutter(supervisorip,vmname='')

if __name__ == '__main__':
    controller = butterflycontroller()

def getunusedport():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('localhost',0))
    addr,port = s.getsockname()
    s.close()
    return port
