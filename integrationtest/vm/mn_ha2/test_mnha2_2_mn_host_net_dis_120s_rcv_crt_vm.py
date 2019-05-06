'''
Test Steps:
    1. disconnect both mn host and recover.
    2. check vip and all service recovered.
    3. create vm to validate everything goes on well. 

@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.node_operations as node_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

vm = None
vip_s_vm_cfg_lst = None
s_vm0 = None
s_vm1 = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    global vip_s_vm_cfg_lst
    global s_vm0
    global s_vm1

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.environ['zstackHaVip']
    vip_s_vm_cfg_lst = test_stub.get_s_vm_cfg_lst_vip_bind(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(vip_s_vm_cfg_lst) != 1:
        test_util.test_fail('vip has been running on %d host(s)' % len(vip_s_vm_cfg_lst))

    s_vm0 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 0)
    s_vm1 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 1)
    test_util.test_logger("disconnect both hosts [%s] and [%s]" % (s_vm0.ip_, s_vm1.ip_))

    test_stub.down_host_network(s_vm0.ip_, test_lib.all_scenario_config, "managment_net")  
    test_stub.down_host_network(s_vm1.ip_, test_lib.all_scenario_config, "managment_net")  
    time.sleep(120)
    test_stub.up_host_network(s_vm0.ip_, test_lib.all_scenario_config, "managment_net")  
    test_stub.up_host_network(s_vm1.ip_, test_lib.all_scenario_config, "managment_net")  
    time.sleep(10)

    vip_s_vm_cfg_lst_new = test_stub.get_s_vm_cfg_lst_vip_bind(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(vip_s_vm_cfg_lst_new) != 1:
        test_util.test_fail('vip has been running on %d host(s)' % len(vip_s_vm_cfg_lst_new))

    test_stub.wrapper_of_wait_for_management_server_start(600)

    test_stub.ensure_hosts_connected(exclude_host=[vip_s_vm_cfg_lst[0]])
    test_stub.ensure_bss_connected(exclude_host=[vip_s_vm_cfg_lst[0]])
    #test_stub.ensure_pss_connected()

    vm = test_stub.create_basic_vm()
    vm.check()
    vm.destroy()

    test_util.test_pass('Create VM Test Success')

#Will be called what ever test result is
def env_recover():
    global s_vm0
    global s_vm1
    test_util.test_logger("up host: %s and %s" % (s_vm0.ip_, s_vm1.ip_))
    test_stub.up_host_network(s_vm0.ip_, test_lib.all_scenario_config, "managment_net")  
    test_stub.up_host_network(s_vm1.ip_, test_lib.all_scenario_config, "managment_net")  
    #test_stub.wait_for_mn_ha_ready(test_lib.all_scenario_config, test_lib.scenario_file)
    test_stub.exec_zsha2_version(vip_s_vm_cfg_lst[0].ip_, "root", "password")

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
