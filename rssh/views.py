# Create your views here.


import re
from libvirt import libvirtError

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

import json
import time

from servers.models import Compute
from vrtManager.hostdetails import wvmHostDetails
from webvirtmgr.settings import TIME_JS_REFRESH


def rssh(request, host_id):
    """
    ssh remote connect host page.
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    if not request.user.is_staff:
        raise PermissionDenied

    errors = []
    time_refresh = TIME_JS_REFRESH

    compute = Compute.objects.get(id=host_id)

    try:
        conn = wvmHostDetails(compute.hostname,
                              compute.login,
                              compute.password,
                              compute.type,
                              compute.hypervisor)
        hostname, host_arch, host_memory, logical_cpu, model_cpu, uri_conn = conn.get_node_info()
        hypervisor = conn.hypervisor_type()
        mem_usage = conn.get_memory_usage()
        ip = compute.hostname
        conn.close()
    except libvirtError as err:
        errors.append(err)

    return render_to_response('rssh.html', locals(), context_instance=RequestContext(request))
