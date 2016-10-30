# Create your views here.

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from instance.models import Instance
from servers.models import Compute
from vrtManager import lxconsole
import zmq


def start_lxconsole(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'GET':
        token = request.GET.get('token', '')
    temptoken = token.split('-', 1)
    host_id = int(temptoken[0])
    uuid = temptoken[1]
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:33456')
    compute = Compute.objects.get(id=host_id)
    vm = Instance.objects.get(uuid=uuid)
    data = str(compute.hostname)+','+str(vm.name)
    socket.send(data)
    port = socket.recv()
    server_ip = str(request.META['HTTP_HOST']).split(':')[0]
    return redirect('http://'+server_ip+':'+port)
