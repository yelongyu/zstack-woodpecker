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

def check_chrony_status(node_ip, port):
    test_util.test_dsc("Check all hosts chrony status.")
    node_ip = node_ip
    port = port
    cmd1 = "chronyc tracking"
    cmd2 = "chronyc sources"
    (retcode1, output, erroutput) = ssh.execute(cmd1, node_ip, 'root', 'password', True, port)
    (retcode2, output, erroutput) = ssh.execute(cmd2, node_ip, 'root', 'password', True, port)
    if retcode1 == 0 and retcode2 == 0:
        test_util.test_logger('@@@DEBUG-> check chrony "chronyc tracking", "chronyc sources" pass')
    else:
        test_util.test_fail('@@@DEBUG-> check chrony "chronyc tracking", "chronyc sources" failed.')

def test():
    test_util.test_dsc("check all hosts chrony status")
    host_uuid_list = []
    host_ip_list = []
    host_port_list = []
    hosts = {}

    for host_id in range(len(res_ops.query_resource(res_ops.HOST))):
        managementIp = res_ops.query_resource(res_ops.HOST)[host_id].managementIp
        sshPort = res_ops.query_resource(res_ops.HOST)[host_id].sshPort
        uuid = res_ops.query_resource(res_ops.HOST)[host_id].uuid
        host_ip_list.append(managementIp)
        host_port_list.append(sshPort)
        host_uuid_list.append(uuid)
    hosts = dict(zip(host_ip_list, host_port_list))
    print "hosts is %s" %(hosts)
    for k, v in hosts.items():
        check_chrony_status(k, v)
    for host_uuid in host_uuid_list:
        host_ops.reconnect_host(host_uuid)
        time.sleep(5)
    for k, v in hosts.items():
        check_chrony_status(k, v)

    host_ops.change_host_state(host_uuid_list[0], "disable")
    for k, v in hosts.items():
        check_chrony_status(k, v)
    host_ops.change_host_state(host_uuid_list[0], "enable")

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Test chrony Success')

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
