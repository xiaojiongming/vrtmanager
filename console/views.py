import re

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.shortcuts import redirect

from vrtManager.instance import wvmInstance
from vrtManager import lxconsole

from servers.models import Compute
from instance.models import Instance

from webvirtmgr.settings import WS_PORT
from webvirtmgr.settings import WS_PUBLIC_HOST

def console(request):
    """
    Console instance block
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'GET':
        token = request.GET.get('token', '')

    temptoken = token.split('-', 1)
    host_id = int(temptoken[0])
    uuid = temptoken[1]
    compute = Compute.objects.get(id=host_id)
    vm = Instance.objects.get(uuid=uuid)

    try:
        temptoken = token.split('-', 1)
        host = int(temptoken[0])
        uuid = temptoken[1]
        instance = Instance.objects.get(compute_id=host, uuid=uuid)
        conn = wvmInstance(instance.compute.hostname,
                           instance.compute.login,
                           instance.compute.password,
                           instance.compute.type,
                           instance.name,
                           instance.compute.hypervisor)
        console_type = conn.get_console_type()
        console_websocket_port = conn.get_console_websocket_port()
        console_passwd = conn.get_console_passwd()
    except:
        console_type = None
        console_websocket_port = None
        console_passwd = None

    ws_port = console_websocket_port if console_websocket_port else WS_PORT
    ws_host = WS_PUBLIC_HOST if WS_PUBLIC_HOST else request.get_host()

    if ':' in ws_host:
        ws_host = re.sub(':[0-9]+', '', ws_host)

    if console_type == 'vnc':
        response = render_to_response('console-vnc.html', locals(),
                                      context_instance=RequestContext(request))
    elif console_type == 'spice':
        response = render_to_response('console-spice.html', locals(),
                                      context_instance=RequestContext(request))
    else:
        response = "Console type %s no support" % console_type

    response.set_cookie('token', token)
    return response
