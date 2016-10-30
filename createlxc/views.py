# Create your views here.

import time

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from libvirt import libvirtError

import ansiblefunc.ans_func
from create.forms import NewVMForm
from servers.models import Compute
from vrtManager import util
from vrtManager.create import wvmCreate


def createlxc(request, host_id):
    """
    Create new lxc container instance.
    """

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    if not request.user.is_staff:
        raise PermissionDenied

    conn = None
    errors = []
    storages = []
    networks = []
    compute = Compute.objects.get(id=host_id)
    instances = None
    wmstorage =None
    templatedb = {}
    templatelist = []
    with open('/var/www/webvirtmgr/ansiblefunc/playbook/template','r') as template:
        lines = template.readlines()
        for line in lines:
            templatedb[line.split(',')[0]] = line.split(',')[1].strip()
            templatelist.append(line.split(',')[0])
    try:
        conn = wvmCreate(compute.hostname,
                         compute.login,
                         compute.password,
                         compute.type,
                         compute.hypervisor)

        storages = sorted(conn.get_storages())
        networks = sorted(conn.get_networks())
        instances = conn.get_instances()
        get_images = sorted(conn.get_storages_images())
        get_containtype = sorted(['operation system','application'])
        mac_auto = util.randomMAC()
    except libvirtError as err:
        errors.append(err)
    if conn:
        if not storages:
            msg = _("You haven't defined have any storage pools")
            errors.append(msg)
        if not networks:
            msg = _("You haven't defined have any network pools")
            errors.append(msg)
        if request.method == 'POST':
            if 'create' in request.POST:
                volumes = {}
                pathtuple=[]
                form = NewVMForm(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
                    if data['meta_prealloc']:
                        meta_prealloc = True
                    if data['name'] in instances:
                        msg = _("A virtual machine with this name already exists")
                        errors.append(msg)
                    if not data['images']:
                        msg = _("First you need to create or select an image")
                        errors.append(msg)
                    if not errors:
                        for vol in data['images'].split(','):
                            try:
                                path = conn.get_volume_path(vol)
                                volumes[path] = conn.get_volume_type(path)
                                pathtuple.append(path)
                            except libvirtError as msg_error:
                                errors.append(msg_error.message)
                        if not errors:
                            uuid = util.randomUUID()
                            try:
                                root = data['images'].split(',')[0]
                                print root
                                rootimage = conn.get_volume_path(root)
                                ostype={'os':'/sbin/init','app':'/bin/sh'}
                                if not data['template']:
                                    lxcdeployjob = ansiblefunc.ans_func.AnsDeployJob(vmname=data['name'],memory=data['memory'],rootimage=rootimage,supervisorip=
                                                                      conn.host,network=data['networks'].split(','),inittype=ostype[form.data['containtype']],
                                                                      rootpass=form.data['rootpass'],cpu=form.data['vcpu'],installedpackage=form.data['packages'],
                                                                      images=pathtuple[1:])
                                else:
                                    lxcdeployjob = ansiblefunc.ans_func.AnsDeployJob(vmname=data['name'],
                                                                                     memory=data['memory'],
                                                                                     rootimage=rootimage, supervisorip=
                                                                                     conn.host,
                                                                                     network=data['networks'].split(
                                                                                         ','),
                                                                                     rootpass=form.data['rootpass'],
                                                                                     cpu=form.data['vcpu'],
                                                                                     images=[],
                                                                                     templatename=data['template'])
                                lxcdeployjob.deploy()
                                time.sleep(2)
                                return HttpResponseRedirect(reverse('instances', args=[host_id]))
                            except libvirtError as err:
                                if data['hdd_size']:
                                    conn.delete_volume(volumes.keys()[0])
                                errors.append(err)

    conn.close()
    return render_to_response('createlxc.html', locals(), context_instance=RequestContext(request))
