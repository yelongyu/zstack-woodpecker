'''
Test case for checking ntp is correct setup
@author: quarkonics
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():
    test_util.test_dsc('Test Host ntp')
    cmd = 'hostname'
    mn = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0]
    for host in test_lib.lib_get_all_hosts_from_plan():
        if mn.hostName == host.managementIp_:
            mn_hostname = test_lib.lib_execute_ssh_cmd(host.managementIp_, host.username_, host.password_, cmd, timeout=30).strip()

    cmd = 'ntpq -p'
    for host in test_lib.lib_get_all_hosts_from_plan():
        if host.managementIp_ == mn_hostname:
            output = test_lib.lib_execute_ssh_cmd(host.managementIp_, host.username_, host.password_, cmd, timeout=30)
            if output.find(mn_hostname) >= 0:
                test_util.test_fail('if host and MN are same host, its not expected to use itself')
        else:
            output = test_lib.lib_execute_ssh_cmd(host.managementIp_, host.username_, host.password_, cmd, timeout=30)
            if output.find(mn_hostname) < 0:
                test_util.test_fail('all host expect to use MN ntp service')

    test_util.test_pass('Test Host ntp Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
