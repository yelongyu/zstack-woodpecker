'''

Integration Test for the status about never stop KVM VM in MN HA mode with all mn hosts shutdown and recovery.

@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.node_operations as node_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import random
import time
import os

vm = None
mn_host_list = None
need_recover_mn_host_list = None

test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    global mn_host_list
    global need_recover_mn_host_list

    must_ps_list = ['MiniStorage']
    test_lib.skip_test_if_any_ps_not_deployed(must_ps_list)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.environ['zstackHaVip']

    test_stub.ensure_hosts_connected()
    test_stub.ensure_bss_connected()
    test_stub.ensure_pss_connected()

    mn_host_list = test_stub.get_mn_host(test_lib.all_scenario_config, test_lib.scenario_file)
    mn_host_num = len(mn_host_list)
    test_mn_host_list = random.sample(range(mn_host_num), (mn_host_num + 1) / 2)


    vm = test_stub.create_basic_vm()
    vm.check()
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    vm.set_state(vm_header.RUNNING)
    vm.check()


    for host in mn_host_list:
        test_util.test_logger("shutdown host [%s]" % (host.ip_))
        test_stub.stop_host(host, test_lib.all_scenario_config)

    need_recover_mn_host_list = range(mn_host_num)

    test_util.test_logger("wait 10s for MN VM to stop")
    time.sleep(10)

    for index in test_mn_host_list:
        test_util.test_logger("recover host [%s]" % (mn_host_list[index].ip_))
        test_stub.recover_host(mn_host_list[index], test_lib.all_scenario_config, test_lib.deploy_config)
        need_recover_mn_host_list.remove(index)

    test_util.test_logger("wait for 20 seconds to see if management node VM starts on any host")
    time.sleep(20)

    test_stub.wrapper_of_wait_for_management_server_start(600)

    test_util.test_logger("Delay 60s and then check if the vm is running")
    time.sleep(180)
    if test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, '22', 300):
        vm.update()
        vm.check()
        vm.destroy()
    else:
        test_util.test_fail("ha vm has not changed to running after 2 hosts recover with 300s")
    test_util.test_pass('Check Never Stop VM Test Success')

#Will be called what ever test result is
def env_recover():
    if need_recover_mn_host_list:
        for index in need_recover_mn_host_list:
            test_util.test_logger("recover host: %s" % (mn_host_list[index].ip_))
            test_stub.recover_host(mn_host_list[index], test_lib.all_scenario_config, test_lib.deploy_config)
    test_stub.wait_for_mn_ha_ready(test_lib.all_scenario_config, test_lib.scenario_file)

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
