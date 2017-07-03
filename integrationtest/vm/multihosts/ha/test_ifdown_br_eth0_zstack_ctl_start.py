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
import threading
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_host = None
mn_ip = None
host_list = None


def async_ifconfig_br_eth0_down_up_wrapper(sleep_time, ip, host_username, host_password):
    cmd = "ifconfig br_zsn0 down; sleep %s; ifconfig br_zsn0 up" %(sleep_time)
    test_lib.lib_execute_ssh_cmd(ip, host_username, host_password, cmd,  timeout=sleep_time+20)
        
    
def add_default_route(ip):
    #this function should not be invoked to recover the env.
    host_username = os.environ.get('hostUsername')
    host_password = os.environ.get('hostPassword')
    cmd = "ip r add default dev br_zsn0 via 172.20.0.1"
    test_lib.lib_execute_ssh_cmd(ip, host_username, host_password, cmd,  timeout = 20)
    


def test():
    global test_host
    global mn_ip
    global host_list

    allow_ps_list = [inventory.LOCAL_STORAGE_TYPE]
    test_lib.skip_test_when_ps_type_not_in_list(allow_ps_list)

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
    if not test_lib.lib_execute_ssh_cmd(mn_ip, host_username, host_password, cmd,  timeout = 120):
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, mn_ip))

    t = threading.Thread(target=async_ifconfig_br_eth0_down_up_wrapper, 
                         args=(240, test_host.ip_, host_username, host_password))
    t.start()

    cmd = "nohup zstack-ctl start &"
    if not test_lib.lib_execute_ssh_cmd(mn_ip, host_username, host_password, cmd,  timeout = 120):
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, mn_ip))
    t.join()

    test_util.test_pass('Test zstack-ctl start when host status is not conformance with zstack db Success')


#Will be called only if exception happens in test().
def error_cleanup():
    pass


def env_recover():
    global host_list
    global test_host
    if host_list and mn_ip and test_host:
        for host in host_list:
            if host.ip_ == mn_ip:
                mn_host = host
                break
        test_util.test_logger("recover host: %s" % (mn_host.ip_))
        #test_stub.recover_host(test_host, test_lib.all_scenario_config, test_lib.deploy_config)
        add_default_route(test_host.ip_)
