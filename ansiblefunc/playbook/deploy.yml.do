---
- hosts: 10.101.11.6
  tasks:
    - name: prepare {{ vmname }} dir
      file: path=/mnt/{{ vmname }} state=directory mode=0755
    - name: format {{ rootimage }}
      filesystem: fstype=ext4 dev={{ rootimage }}
    - name: mount {{ rootimage }} ==> /mnt/{{ vmname }}
      mount: 
        name: /mnt/{{ vmname }}
        src: "{{ rootimage }}"
        fstype: ext4
        opts: rw
        state: mounted
    - name: check dir alread have file
      stat: path=/mnt/{{ vmname }}/etc
      register: havefile
    - name: untar
      unarchive: src={{ template }} dest=/mnt/{{ vmname }}/ 
    - name: check basic filesystem ok
      stat: path=/mnt/{{ vmname }}/etc
      register: filesystemok

    - name: allow root login,set root passwd with {{ rootpass }}
      shell: echo -e "pts/0\npts/1\npts/2\npts/3\n"  >>  /mnt/{{ vmname }}/etc/securetty
      when: filesystemok.stat.exists
    - name:
      shell: chroot /mnt/{{vmname}} /bin/bash -c "echo \"{{ rootpass }}\" | /usr/bin/passwd --stdin root"
      when: filesystemok.stat.exists
    - name: set hostname and network
      shell: echo -e "NETWORKING=yes \nHOSTNAME={{ vmname }}" > /mnt/{{ vmname }}/etc/sysconfig/network
      when: filesystemok.stat.exists
    - shell: echo -e "{{ vmname }}" > /mnt/{{ vmname }}/etc/hostname
      when: filesystemok.stat.exists
    - shell: echo -e "BOOTOROTO=dhcp \nONBOOT=yes \nDEVICE=eth0" > /mnt/{{ vmname }}/etc/sysconfig/network-scripts/ifcfg-eth0
      when: filesystemok.stat.exists
    - name: generate {{ vmname }}.xml
      file: path=/xml state=directory
    - template: src=./lxc.xml.j2 dest=/xml/{{ vmname }}.xml
    - name: deploy to supervisor
      command: virsh -c lxc:/// define /xml/{{ vmname }}.xml
 
