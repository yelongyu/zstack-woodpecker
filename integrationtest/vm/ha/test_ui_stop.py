'''

Integration Test for HA mode with UI stop on one node.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

node_ip = None

def test():
    global node_ip
    node_ip = os.environ.get('node1Ip')
    test_util.test_logger("stop ui on node: %s" % (node_ip))
    cmd = "zstack-ctl stop_ui"
    host_username = os.environ.get('nodeUserName')
    host_password = os.environ.get('nodePassword')
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)
    test_util.test_logger("check if it still works")
    zstack_ha_vip = os.environ.get('zstackHaVip')
    if not test_lib.lib_network_check(zstack_ha_vip, 8200):
        test_util.test_fail('Could not access UI through VIP: %s, port: 8200' % (zstack_ha_vip))
    cmd = "zstack-ctl start_ui"
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)

    test_util.test_pass('Create VM Test UI Stop on one node Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global node_ip
    cmd = "zstack-ctl start_ui"
    host_username = os.environ.get('nodeUserName')
    host_password = os.environ.get('nodePassword')
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)

