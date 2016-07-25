'''

Integration Test for creating KVM VM in HA mode with one node network down for a while.

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

vm = None
node_ip = None

def test():
    global vm
    global node_ip
    node_ip = os.environ.get('node1Ip')
    test_util.test_logger("shutdown node network for a small while: %s" % (node_ip))
    l2_network_interface = os.environ.get('l2ManagementNetworkInterface')
    cmd = "ifdown %s && sleep 10 && ifup %s" % (l2_network_interface, l2_network_interface)
    host_username = os.environ.get('nodeUserName')
    host_password = os.environ.get('nodePassword')
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)
    test_util.test_logger("recover mysql")
    cmd = "service mysql start"
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)
    time.sleep(60)
    test_stub.exercise_connection(600)

    test_util.test_logger("check create vm")
    vm = test_stub.create_basic_vm()
    vm.check()
    vm.destroy()

    test_util.test_pass('Create VM Test with one node network down for a while Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
