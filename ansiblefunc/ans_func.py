import os
import sys
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.inventory import host
from ansible.executor.playbook_executor import PlaybookExecutor


class AnsDeployJob:
    def __init__(self, vmname, memory, rootimage, supervisorip,
                 network,images
                 ,inittype='/sbin/init',
                 rootpass='Abc,123.', cpu='1',
                 playbook='/var/www/webvirtmgr/ansiblefunc/playbook/deploy.yml.do',
                 installedpackage='',templatename=''
                 ):
        self._installedpackage = 'systemd passwd yum centos-release vim openssh-server procps-ng iproute net-tools dhclient less '+installedpackage
        self._keyfile = '/var/www/webvirtmgr/ansiblefunc/playbook/id_rsa.key'
        self._vmname = vmname
        self._memory = int(memory)*1024
        self._rootimage = rootimage
        self._network = network
        self._supervisorip = supervisorip
        self._inittype = inittype
        self._network =network
        self._rootpass = rootpass
        self._cpu = cpu
        self._playbook = playbook
        self._images = images
        self._templatename = templatename
        deploy_method={'custom':'/var/www/webvirtmgr/ansiblefunc/playbook/deploy.yml.do','template':'/var/www/webvirtmgr/ansiblefunc/playbook/deploy_templ.yml.do'}

    def deploy(self):
        templatedb = {}
        if self._templatename:
            with open('/var/www/webvirtmgr/ansiblefunc/playbook/template','r') as template:
                lines = template.readlines()
                for line in lines:
                    templatedb[line.split(',')[0]] = line.split(',')[1]
                with open('/var/www/webvirtmgr/ansiblefunc/playbook/deploy_templ.yml','r') as source:
                    lines = source.readlines()
                    with open('/var/www/webvirtmgr/ansiblefunc/playbook/deploy.yml.do', 'w') as dest:
                        for line in lines:
                            dest.write(line.replace('!host!', self._supervisorip))
        else:
            with open('/var/www/webvirtmgr/ansiblefunc/playbook/deploy.yml','r') as source:
                lines = source.readlines()
                with open('/var/www/webvirtmgr/ansiblefunc/playbook/deploy.yml.do','w') as dest:
                    for line in lines:
                        dest.write(line.replace('!host!',self._supervisorip))
        variable_manager = VariableManager()
        loader = DataLoader()
        supervisor =host.Host(name=self._supervisorip,port=None)
        variable_manager.set_host_variable(supervisor,'vmname',self._vmname)
        variable_manager.set_host_variable(supervisor, 'rootpass', self._rootpass)
        variable_manager.set_host_variable(supervisor, 'memory', self._memory)
        variable_manager.set_host_variable(supervisor, 'cpu', self._cpu)
        variable_manager.set_host_variable(supervisor, 'rootimage', self._rootimage)
        variable_manager.set_host_variable(supervisor, 'network', self._network)
        variable_manager.set_host_variable(supervisor, 'inittype', self._inittype)
        variable_manager.set_host_variable(supervisor, 'images', self._images)
        if not self._templatename:
            variable_manager.set_host_variable(supervisor, 'installedpackage', self._installedpackage)
        else:
            variable_manager.set_host_variable(supervisor, 'template', templatedb[self._templatename].strip())
        inventory = Inventory(loader=loader, variable_manager=variable_manager,
                              host_list='/var/www/webvirtmgr/ansiblefunc/playbook/hosts')

        if not os.path.exists(self._playbook):
            print 'playbook not found'
            sys.exit()
        options_tuple = namedtuple('Options',
                             ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path', 'forks',
                              'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
                              'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
        options = options_tuple(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                          module_path=None, forks=100, remote_user='root', private_key_file=self._keyfile,
                          ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None,
                          become=True, become_method=None, become_user='root', verbosity=None, check=False)
        variable_manager.extra_vars = {'hosts': self._supervisorip}
        pbex = PlaybookExecutor(playbooks=[self._playbook], inventory=inventory, variable_manager=variable_manager,
                                loader=loader, options=options, passwords={})
        results = pbex.run()
        print results

