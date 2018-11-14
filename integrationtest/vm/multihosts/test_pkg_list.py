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
        flag = 0
        output = os.system("cat /etc/redhat-release |awk '{print $4}' |awk -F '.' '{print $2}'")
        print type(output)
        if output == 4:
            flag = 1

        mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
        hosts = res_ops.query_resource(res_ops.HOST, [], None)
        for host in hosts:
            host_ip = host.managementIp
            if host_ip != mn_ip:
                cmd = 'rpm -qa > rpm_list_after.txt;pip list > pip_list_after.txt'
                test_lib.lib_execute_ssh_cmd(host.managementIp_, 'root', 'password', cmd, 180)
                cmd = "diff /root/rpm_list.txt /root/rpm_list_after.txt |grep '<\|>' > change_list.txt"
                test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', cmd, 180)
                cmd = "diff /root/pip_list.txt /root/pip_list_after.txt |grep '<\|>' >> change_list.txt"
                test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', cmd, 180)
            
                if flag != 1:
                    cmd = "diff /home/c74_expect_pkg_list.txt /root/change_list.txt"
                    output = test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', cmd, 180)            
                    if output != "":
                        test_util.test_fail('Host pkg list changed after been added in MN')
                else:
                    cmd = "diff /home/c72_expect_pkg_list.txt /root/change_list.txt"
                    output = test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', cmd, 180)
                    if output != "":
                        test_util.test_fail('Host pkg list changed after been added in MN')
  
#Will be called only if exception happens in test().
def error_cleanup():
    pass
