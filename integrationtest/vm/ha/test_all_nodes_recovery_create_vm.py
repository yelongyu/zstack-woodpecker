'''

Integration Test for creating KVM VM with all nodes shutdown and recovered.

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

def test():
    global vm
    cmd = "init 0"
    host_username = os.environ.get('nodeUserName')
    host_password = os.environ.get('nodePassword')
    zstack_ha_vip = os.environ.get('zstackHaVip')
    node1_ip = os.environ.get('node1Ip')
    test_util.test_logger("shutdown node: %s" % (node1_ip))
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    node2_ip = os.environ.get('node2Ip')
    test_util.test_logger("shutdown node: %s" % (node2_ip))
    rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)

    test_util.test_logger("recover node: %s" % (node1_ip))
    os.system('bash -ex %s %s' % (os.environ.get('nodeRecoverScript'), node1_ip))
    test_util.test_logger("recover node: %s" % (node2_ip))
    os.system('bash -ex %s %s' % (os.environ.get('nodeRecoverScript'), node2_ip))

    test_util.test_dsc('Delete /var/lib/zstack/ha/ha.yaml, recover ha with zstack-ctl recover_ha, expect to fail')
    cmd = "rm /var/lib/zstack/ha/ha.yaml"
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    if not rsp:
        rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)

    cmd = "zstack-ctl recover_ha"
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    if not rsp:
        rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)
    if rsp == False:
        test_util.test_logger("Cannot recover ha without /var/lib/zstack/ha/ha.yaml when use zstack-ctl recover_ha, expect to False")
    else:
	test_util.test_fail('Expect to False, but get the different result when recover ha without /var/lib/zstack/ha/ha.yaml by using zstack-ctl recover_ha')

    test_util.test_dsc('Recover with zstack-ctl install_ha, expect to pass')
    cmd = "zstack-ctl install_ha --host1-info %s:%s@%s --host2-info %s:%s@%s --vip %s --recovery-from-this-host" % \
            (host_username, host_password, node1_ip, host_username, host_password, node2_ip, zstack_ha_vip)
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    if not rsp:
        rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)
    time.sleep(180)
    test_stub.exercise_connection(600)

    vm = test_stub.create_basic_vm()
    vm.check()
    vm.destroy()

    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
