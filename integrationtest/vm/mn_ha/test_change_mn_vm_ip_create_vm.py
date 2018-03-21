'''

Integration Test for creating KVM VM in MN HA mode after change mn vm's IP.

@author: Mirabel
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.node_operations as node_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import test_stub
import time
import os

vm = None
ori_ip = None
mn_vm_host = None

def test():
    global vm
    global ori_ip
    global mn_vm_host
    mn_vm_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(mn_vm_host) != 1:
        test_util.test_fail('MN VM is running on %d host(s)' % len(mn_vm_host))

    test_util.test_logger("change mn vm ip in config file of host [%s]" % (mn_vm_host[0].ip_))
    new_mn_vm_ip = "172.20.199.99"
    ori_ip = os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_IP')
    test_stub.update_mn_vm_config(mn_vm_host[0], 'Ipaddr', new_mn_vm_ip, test_lib.all_scenario_config)
    test_stub.destroy_mn_vm(mn_vm_host[0], test_lib.all_scenario_config)
    test_util.test_logger("wait for 40 seconds to see if management node VM starts on another host")
    time.sleep(40)
    try:
        new_mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
        if len(new_mn_host) == 0:
            test_util.test_fail("management node VM does not start after change ip and destroyed")
        elif len(new_mn_host) > 1:
            test_util.test_fail("management node VM starts on more than one host after change ip and destroyed")
    except:
        test_util.test_fail("management node VM does not start after change ip and destroyed")
    if new_mn_host[0].ip_ != mn_vm_host[0].ip_:
        test_util.test_fail('management node VM starts on another host after change ip and destroyed')

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = new_mn_vm_ip
    test_util.test_logger("wait for 5 minutes to see if management node starts again")
    #node_ops.wait_for_management_server_start(300)
    test_stub.wrapper_of_wait_for_management_server_start(600)

    test_stub.ensure_hosts_connected()
    test_stub.ensure_pss_connected()
    test_stub.ensure_bss_connected()

    test_stub.return_pass_ahead_if_3sites("TEST PASS") 
    vm = test_stub.create_basic_vm()
    vm.check()
    vm.destroy()
    test_util.test_pass('Create VM Test Success')

#Will be called what ever test result is
def env_recover():
    if ori_ip:
        test_util.test_logger("change mn vm's ip to original one: %s" % (ori_ip))
        test_stub.update_mn_vm_config(mn_vm_host[0], 'Ipaddr', ori_ip, test_lib.all_scenario_config)
        test_stub.destroy_mn_vm(mn_vm_host[0], test_lib.all_scenario_config)
        os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = ori_ip
        try:
            node_ops.wait_for_managemnet_server_start(300)
        except:
            test_util.test_logger("change mn vm's ip to original one failes")

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
