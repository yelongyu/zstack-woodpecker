'''
New Integration Test for test host chrony.
Test step:
    1.Check chrony on all host
    2.Reconnect all hosts and check all hosts's chrony again
    3.disable mn node and check again

@author: Pengtao.Zhang
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstacklib.utils.ssh as ssh
import apibinding.inventory as inventory
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def check_chrony_status(node_ip):
    test_util.test_dsc("Check all hosts chrony status.")
    node_ip = node_ip
    cmd1 = "chronyc tracking"
    cmd2 = "chronyc sources"
    (retcode1, output, erroutput) = ssh.execute(cmd1, node_ip, 'root', 'password', True, 22)
    (retcode2, output, erroutput) = ssh.execute(cmd2, node_ip, 'root', 'password', True, 22)
    if retcode1 == 0 and retcode2 == 0:
        test_util.test_logger('@@@DEBUG-> check chrony "chronyc tracking", "chronyc sources" pass')
    else:
        test_util.test_fail('@@@DEBUG-> check chrony "chronyc tracking", "chronyc sources" failed.')

def test():
    test_util.test_dsc("check all hosts chrony status")
    host_uuid_list = []
    host_ip_list = []
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    host_list = test_lib.lib_get_all_hosts_from_plan()
    for host in host_list:
        host_ip = host.managementIp_
        host_hostname = host_ip.replace('.', '-')
        host_uuid = test_lib.lib_get_host_by_ip(host_ip).uuid
        host_uuid_list.append(host_uuid)
        host_ip_list.append(host_ip)
    for ip in host_ip_list:
        check_chrony_status(ip)
    for host_uuid in host_uuid_list:
        host_ops.reconnect_host(host_uuid)
        time.sleep(5)
    for ip in host_ip_list:
        check_chrony_status(ip)
    host_ops.change_host_state(host_uuid_list[0], "disable")
    check_chrony_status(host_ip_list[0])
    host_ops.change_host_state(host_uuid_list[0], "enable")

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Test prometheus Success')

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
