# Create your views here.

from vrtManager.rssh import rssh
from django.shortcuts import redirect
import zmq

def connect(request,ip):
    server_ip = str(request.META['HTTP_HOST']).split(':')[0]
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:33456')
    data = str(ip)+','
    socket.send(data)
    port = socket.recv()
    return redirect('http://'+server_ip+':'+str(port))
