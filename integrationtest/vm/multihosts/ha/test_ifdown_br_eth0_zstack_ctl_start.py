'''
New Integration Test for zstack-ctl start normally when host status is not comformance with last boot up record.
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import apibinding.inventory as inventory
import time
import os

test_host = None

def test():
    global test_host

    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    host_list = test_stub.get_sce_hosts(test_lib.all_scenario_config, test_lib.scenario_file)
    for host in host_list:
        if host.ip_ != mn_ip:
            test_host = host
            break
    if not test_host:
        test_util.test_fail('there is no host with ip excluding mn_ip: %s in scenario file.' %(mn_ip))

    host_username = os.environ.get('hostUsername')
    host_password = os.environ.get('hostPassword')

    cmd = "zstack-ctl stop"
    test_lib.lib_execute_ssh_cmd(mn_ip, host_username, host_password, cmd, 120)

    cmd = "ifdown br_eth0"
    test_lib.lib_execute_ssh_cmd(test_host.ip_, host_username, host_password, cmd, 10)

    cmd = "zstack-ctl start"
    test_lib.lib_execute_ssh_cmd(mn_ip, host_username, host_password, cmd, 300)

    cmd = "ifup br_eth0"
    test_lib.lib_execute_ssh_cmd(test_host.ip_, host_username, host_password, cmd, 10)

    test_util.test_pass('Test zstack-ctl start when host status is not conformance with zstack db Success')


#Will be called only if exception happens in test().
def error_cleanup():
    pass


def env_recover():
    global test_host
    test_util.test_logger("recover host: %s" % (test_host.ip_))
    test_stub.recover_host(test_host, test_lib.all_scenario_config, test_lib.deploy_config)
