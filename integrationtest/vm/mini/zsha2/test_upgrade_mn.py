'''
Test Steps:
    1. upgrade mn in host where vip located.
    2. check vip switch to another MN.

@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.node_operations as node_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import sys

vm = None
vip_s_vm_cfg_lst = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    global vip_s_vm_cfg_lst

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.environ['zstackHaVip']

    test_stub.ensure_hosts_connected()
    test_stub.ensure_bss_connected()
    test_stub.ensure_pss_connected()
    vm = test_stub.create_basic_vm()

    vip_s_vm_cfg_lst = test_stub.get_s_vm_cfg_lst_vip_bind(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(vip_s_vm_cfg_lst) != 1:
        test_util.test_fail('vip has been running on %d host(s)' % len(vip_s_vm_cfg_lst))

    test_util.test_logger("disconnect host [%s]" % (vip_s_vm_cfg_lst[0].ip_))
    #test_stub.down_host_network(vip_s_vm_cfg_lst[0].ip_, test_lib.all_scenario_config, "managment_net")  

    buildtype = test_stub.get_buildtype_by_sce_file(test_lib.scenario_file)
    buildid = test_stub.get_buildid_by_sce_file(test_lib.scenario_file)
    build_server = os.environ.get('BUILD_SERVER')

    cmd = "cd /root/mirror/" + buildtype+ "/" + buildid + "/ && ls ZStack*-installer-*.bin"
    zstack_bin_name = test_lib.lib_execute_ssh_cmd(build_server, "root", "password", cmd).replace("\n", "")

    zstack_bin_path = "/root/" + zstack_bin_name
    cmd = "wget -c http://" + build_server + "/mirror/" + buildtype + "/" + buildid + "/" + zstack_bin_name + " -O " + zstack_bin_path
    test_lib.lib_execute_ssh_cmd(vip_s_vm_cfg_lst[0].ip_, "root", "password", cmd)

    test_stub.exec_upgrade_mn(vip_s_vm_cfg_lst[0].ip_, "root", "password", zstack_bin_path)

    print ":%s:" %(cmd)
    time.sleep(5)

    #expected_vip_s_vm_cfg_lst_ip = test_stub.get_expected_vip_s_vm_cfg_lst_after_switch(test_lib.all_scenario_config, test_lib.scenario_file, vip_s_vm_cfg_lst[0].ip_)
    #if not test_stub.check_if_vip_is_on_host(test_lib.all_scenario_config, test_lib.scenario_file, expected_vip_s_vm_cfg_lst_ip):
    #    test_util.test_fail("find vip should drift on ip %s, but is not on it." %(expected_vip_s_vm_cfg_lst_ip))

    vip_s_vm_cfg_lst_new = test_stub.get_s_vm_cfg_lst_vip_bind(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(vip_s_vm_cfg_lst_new) != 1:
        test_util.test_fail('vip has been running on %d host(s)' % len(vip_s_vm_cfg_lst_new))

    test_stub.wrapper_of_wait_for_management_server_start(600)

    cond = res_ops.gen_query_conditions('uuid', '=', vm.vm.uuid)
    for i in range(0, 60):
        if res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0].state == "Running":
            break
        time.sleep(1)
    vm.destroy()

    test_util.test_pass('Create VM Test Success')

#Will be called what ever test result is
def env_recover():
    test_stub.exec_zsha2_version(vip_s_vm_cfg_lst[0].ip_, "root", "password")
    #test_util.test_logger("recover host: %s" % (vip_s_vm_cfg_lst[0].ip_))
    #test_stub.up_host_network(vip_s_vm_cfg_lst[0].ip_, test_lib.all_scenario_config, "managment_net")  
    #test_stub.recover_host(vip_s_vm_cfg_lst[0], test_lib.all_scenario_config, test_lib.deploy_config)
    #test_stub.wait_for_mn_ha_ready(test_lib.all_scenario_config, test_lib.scenario_file)

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
