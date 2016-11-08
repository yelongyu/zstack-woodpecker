'''
@author: MengLai 
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstacklib.utils.ssh as ssh
import test_stub
import time
import os
import uuid

vm = None

tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()

def test():
    global vm
    global node1_ip
    global node2_ip
    global host_username
    global host_password 

    host_username = os.environ.get('nodeUserName')
    host_password = os.environ.get('nodePassword')
    zstack_ha_vip = os.environ.get('zstackHaVip')
    node1_ip = os.environ.get('node1Ip')
    node2_ip = os.environ.get('node2Ip')

    test_util.test_dsc('Prepare upgrade package and iso')

    cmd = "scp 192.168.200.1:/httpd/zstack_iso_centos7/latest/test/ZStack-Community-x86_64-DVD-1.4.0.iso /root/" 
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 600)
    rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 600)   
 
    all_in_one_pkg = os.environ['zstackPkg']
    local_ip = os.environ['sftpBackupStorageHostname']
    cmd = "scp %s:%s /root/" % (local_ip, all_in_one_pkg) 
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)

    test_util.test_dsc('Start MN of node1 and node2')
    cmd = "zstack-ctl start"
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 600)
    rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 600)

    iso_path = "/root/ZStack-Community-x86_64-DVD-1.4.0.iso"
    upk_pkg = "/root/zstack-offline-installer-test.bin" 
    test_util.test_dsc('Upgrade HA')
    cmd = "zstack-ctl upgrade_ha --mevoco-installer %s --iso %s" % (upk_pkg, iso_path)
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 1800)
    if not rsp:
        rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 1800)
    time.sleep(180)

    vm = test_stub.create_basic_vm()
    vm.check()
    vm.destroy()

    cmd = "echo 'y' | rm %s" % iso_path
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)

    cmd = "echo 'y' | rm %s" % upk_pkg
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)

    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global node1_ip
    global node2_ip
    global host_username
    global host_password

    if vm:
        try:
            vm.destroy()
        except:
            pass

    cmd = "echo 'y' | rm /root/ZStack-Community-x86_64-DVD-1.4.0.iso"
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)

    cmd = "echo 'y' | rm /root/zstack-offline-installer-test.bin"
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)
