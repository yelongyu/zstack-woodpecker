'''

@author: YYK
'''

import zstacklib.utils.shell as shell
import zstacklib.utils.ssh as ssh
import os.path
import sys

def check_and_install_ansible():
    cmd = 'which ansible'
    try:
        shell.call(cmd)
    except:
        print('ansible is not installed. Will try to install ansible')
        cmd = 'pip install ansible'
        shell.call(cmd)
        print('ansible is installed successfully')

def enable_ansible_connection(target, username, password, exc_info, port): 
    ansible_config = '/etc/ansible/ansible.cfg'
    host_config = '/etc/ansible/hosts'
    ansible_config_content='''
[defaults]
forks = 100
host_key_checking = False
pipelining = True

'''
    add_host_cmd = "grep '^%s$' %s; if [ $? -ne 0 ]; then echo -e '\n%s\n' >> %s; sed -i '/^$/d' %s; fi; " % (target, host_config, target, host_config, host_config)
    if not os.path.exists(os.path.dirname(ansible_config)):
        os.system('mkdir -p %s' % os.path.dirname(ansible_config))
    if not os.path.exists(ansible_config):
        open(ansible_config, 'w').write(ansible_config_content)

    shell.call(add_host_cmd)
    print('Create no ssh password for: %s ' % target)
    try:
        ssh.make_ssh_no_password(target, username, password, port)
    except Exception as e:
        exc_info.append(sys.exc_info())
        raise e

def do_ansible(ansible_dir, ansible_cmd, lib_files, exc_info):
    '''
    If need to execute ansible_cmd for mulitle hosts, the params is like:
    -e 'host=HOST1:HOST2:HOST3 other_args'.

    If Ansible failed, the files in list of lib_files will be deleted from 
    target machine. 
    '''
    print('ansible-playbook -vvvv %s' % ansible_cmd)
    try:
        print  shell.call('cd %s; ansible-playbook -vvvv %s' % (ansible_dir, ansible_cmd))
    except Exception as e:
        for lib_file in lib_files:
            shell.call('/bin/rm -rf /var/lib/zstack/%s' % lib_file) 
        exc_info.append(sys.exc_info())
        raise e

    print('Execute ansible command successfully: ansible-playbook %s ' % ansible_cmd)

def execute_ansible(target, username, password, ansible_dir, ansible_cmd, lib_files = [], exc_info = [], port=22):
    '''
    lib_files is a list includes the file will be copied to target machine by
    ansible. It is usually a file with its parent folder under /var/lib/zstack.
    e.g. [ 'testagent/zstacklib-0.1.0.tar.gz' ]
    '''
    enable_ansible_connection(target, username, password, exc_info, port)
    do_ansible(ansible_dir, ansible_cmd, lib_files, exc_info)
