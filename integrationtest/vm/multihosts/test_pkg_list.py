'''

New Integration test for pkg list

@author: chenyuan.xu
'''
import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import filecmp
import os

def test():
        hosts = res_ops.query_resource(res_ops.HOST, [], None)
        for host in hosts:
            host_ip = host.managementIp
            cmd = 'rpm -qa > rpm_list_after.txt;pip list > pip_list_after.txt'
            test_lib.lib_execute_ssh_cmd(host.managementIp_, 'root', 'password', cmd, 180)
            cmd = "diff /root/rpm_list.txt /root/rpm_list_after.txt"
            output = test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', cmd, 180)
            if output != "":
                test_util.test_fail('host:%s rpm list changed after been added in the mn node.' % host_ip)

            cmd = "diff /root/pip_list.txt /root/pip_list_after.txt"
            output = test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', cmd, 180)
            if output != "":
                test_util.test_fail('host:%s pip list changed after been added in the mn node.' % host_ip)

#Will be called only if exception happens in test().
def error_cleanup():
    pass
