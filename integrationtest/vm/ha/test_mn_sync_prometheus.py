'''

Integration Test for Prometheus Sync in HA mode.

@author: Mirabel
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import time
import os

vm1 = None
vm2 = None
node1_ip = None
node2_ip = None

def test():
    global vm1
    global vm2
    global node1_ip
    global node2_ip

    node1_ip = os.environ.get('node1Ip')
    node2_ip = os.environ.get('node2Ip')

    vm1 = test_stub.create_basic_vm()
    vm2 = test_stub.create_basic_vm()
    vm1.check()
    vm2.check()
    host1_uuid = test_lib.lib_find_host_by_vm(vm1.get_vm()).uuid
    host2_uuid = test_lib.lib_find_host_by_vm(vm2.get_vm()).uuid
    if host1_uuid == host2_uuid:
        test_stub.migrate_vm_to_random_host(vm1)
    host1_uuid = test_lib.lib_find_host_by_vm(vm1.get_vm()).uuid
    vm1.destroy()
    vm2.destroy()
    end_time = int(time.time())

    mn1_host1_data = test_lib.lib_get_host_cpu_prometheus_data(node1_ip, end_time, 200, host1_uuid)
    mn2_host1_data = test_lib.lib_get_host_cpu_prometheus_data(node2_ip, end_time, 200, host1_uuid)
    mn1_host2_data = test_lib.lib_get_host_cpu_prometheus_data(node1_ip, end_time, 200, host2_uuid)
    mn2_host2_data = test_lib.lib_get_host_cpu_prometheus_data(node2_ip, end_time, 200, host2_uuid)
    if cmp(mn1_host1_data,mn2_host1_data) != 0:
        test_util.test_fail('Prometheus Sync Test Fail, host[uuid:%s] data on node:%s is [%s], data on node:%s is [%s]' % (host1_uuid, node1_ip, mn1_host1_data, node2_ip, mn2_host1_data))
    if cmp(mn1_host2_data,mn2_host2_data) != 0:
        test_util.test_fail('Prometheus Sync Test Fail, host[uuid:%s] data on node:%s is [%s], data on node:%s is [%s]' % (host1_uuid, node1_ip, mn1_host2_data, node2_ip, mn2_host2_data))
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
