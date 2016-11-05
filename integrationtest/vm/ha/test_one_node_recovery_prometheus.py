'''

Integration Test for Prometheus Sync in HA mode after one node recover.

@author: Mirabel
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import time
import os

vm = None
node1_ip = None
node2_ip = None

def test():
    global vm
    global node1_ip
    global node2_ip

    node1_ip = os.environ.get('node1Ip')
    node2_ip = os.environ.get('node2Ip')
    test_util.test_logger("shutdown node: %s" % (node1_ip))
    cmd = "init 0"
    host_username = os.environ.get('nodeUserName')
    host_password = os.environ.get('nodePassword')
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    test_util.test_logger("wait for 2 minutes to see if http api still works well")
    time.sleep(180)

    vm = test_stub.create_basic_vm()
    vm.check()
    vm.destroy()
    end_time = int(time.time())

    test_util.test_logger("recover node: %s" % (node1_ip))
    os.system('bash -ex %s %s' % (os.environ.get('nodeRecoverScript'), node1_ip))
    time.sleep(180)

    host_uuid = vm.get_vm().hostUuid
    data1 = test_lib.lib_get_host_cpu_prometheus_data(node1_ip, end_time, 200, host_uuid)
    data2 = test_lib.lib_get_host_cpu_prometheus_data(node2_ip, end_time, 200, host_uuid)
    if cmp(data1,data2) != 0:
        test_util.test_fail('Prometheus Sync Test Fail, data on node:%s is [%s], data on node:%s is [%s]' % (node1_ip, data1, node2_ip, data2))
    test_util.test_pass('Prometheus Sync Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
    test_util.test_logger("recover node: %s" % (node1_ip))
    os.system('bash -ex %s %s' % (os.environ.get('nodeRecoverScript'), node1_ip))
    time.sleep(180)
