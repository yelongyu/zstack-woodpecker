'''
Test Steps:
    1. force stop both mn host and recover.
    2. check vip and all service recovered.
    3. create vm to validate everything goes on well. 

@author: SyZhao
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
vip_s_vm_cfg_lst = None
s_vm0 = None
s_vm1 = None

def test():
    global vm
    global vip_s_vm_cfg_lst
    global s_vm0
    global s_vm1

    vip_s_vm_cfg_lst = test_stub.get_s_vm_cfg_lst_vip_bind(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(vip_s_vm_cfg_lst) != 1:
        test_util.test_fail('vip has been running on %d host(s)' % len(vip_s_vm_cfg_lst))

    s_vm0 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 0)
    s_vm1 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 1)
    test_util.test_logger("force stop both hosts [%s] and [%s]" % (s_vm0.ip_, s_vm1.ip_))
    test_stub.stop_host(s_vm0, test_lib.all_scenario_config, 'cold')
    test_stub.stop_host(s_vm1, test_lib.all_scenario_config, 'cold')
    time.sleep(5)
    test_stub.start_host(s_vm0, test_lib.all_scenario_config)
    test_stub.start_host(s_vm1, test_lib.all_scenario_config)
    recover_vlan_in_host(s_vm0.ip_, test_lib.all_scenario_config, test_lib.deploy_config) 
    recover_vlan_in_host(s_vm1.ip_, test_lib.all_scenario_config, test_lib.deploy_config) 

    vip_s_vm_cfg_lst_new = test_stub.get_s_vm_cfg_lst_vip_bind(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(vip_s_vm_cfg_lst_new) != 1:
        test_util.test_fail('vip has been running on %d host(s)' % len(vip_s_vm_cfg_lst_new))

    test_stub.wrapper_of_wait_for_management_server_start(600)

    test_stub.ensure_hosts_connected(exclude_host=[vip_s_vm_cfg_lst[0]])
    test_stub.ensure_bss_connected()
    test_stub.ensure_pss_connected()

    vm = test_stub.create_basic_vm()
    vm.check()
    vm.destroy()

    test_util.test_pass('Create VM Test Success')

#Will be called what ever test result is
def env_recover():
    global s_vm0
    global s_vm1
    test_util.test_logger("recover host: %s and %s" % (s_vm0.ip_, s_vm1.ip_))
    test_stub.recover_host(s_vm0, test_lib.all_scenario_config, test_lib.deploy_config)
    test_stub.recover_host(s_vm1, test_lib.all_scenario_config, test_lib.deploy_config)
    test_stub.wait_for_mn_ha_ready(test_lib.all_scenario_config, test_lib.scenario_file)

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
