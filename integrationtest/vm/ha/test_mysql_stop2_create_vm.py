'''

Integration Test for creating KVM VM in HA mode with mysql stop on one node.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import test_stub
import time
import os

vm1 = None
vm2 = None
node_ip = None

def test():
    global vm1
    global vm2
    global node_ip
    vm1 = test_stub.create_basic_vm()
    node_ip = os.environ.get('node2Ip')
    test_util.test_logger("stop mysql on node: %s" % (node_ip))
    cmd = "service mysql stop"
    host_username = os.environ.get('nodeUserName')
    host_password = os.environ.get('nodePassword')
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)
    time.sleep(60)
    test_util.test_logger("create vm to check if it still works")
    vm1.check()
    vm1.destroy()
    vm2 = test_stub.create_basic_vm()
    vm2.check()
    vm2.destroy()
    cmd = "service mysql start"
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)
    time.sleep(60)

    test_util.test_pass('Create VM Test Mysql Stop on one node Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm1
    global vm2
    global node_ip
    cmd = "service mysql start"
    host_username = os.environ.get('nodeUserName')
    host_password = os.environ.get('nodePassword')
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)
    time.sleep(60)

    if vm1:
        try:
            vm1.destroy()
        except:
            pass

    if vm2:
        try:
            vm2.destroy()
        except:
            pass
