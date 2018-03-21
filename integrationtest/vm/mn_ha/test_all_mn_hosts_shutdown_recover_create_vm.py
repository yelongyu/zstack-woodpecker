'''

Integration Test for creating KVM VM in MN HA mode with all mn hosts shutdown and recovery.

@author: Mirabel
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.node_operations as node_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import test_stub
import random
import time
import os

vm = None
mn_host_list = None
need_recover_mn_host_list = None

def test():
    global vm
    global mn_host_list
    global need_recover_mn_host_list

    mn_host_list = test_stub.get_mn_host(test_lib.all_scenario_config, test_lib.scenario_file)
    mn_host_num = len(mn_host_list)
    test_mn_host_list = random.sample(range(mn_host_num), (mn_host_num + 1) / 2)

    for host in mn_host_list:
        test_util.test_logger("shutdown host [%s]" % (host.ip_))
        test_stub.stop_host(host, test_lib.all_scenario_config)

    need_recover_mn_host_list = range(mn_host_num)

    test_util.test_logger("wait 10s for MN VM to stop")
    time.sleep(10)
    mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(mn_host) != 0:
        test_util.test_fail('MN VM is still running on %d host(s)' % len(mn_host))

    for index in test_mn_host_list:
        test_util.test_logger("recover host [%s]" % (mn_host_list[index].ip_))
        test_stub.recover_host(mn_host_list[index], test_lib.all_scenario_config, test_lib.deploy_config)
        need_recover_mn_host_list.remove(index)

    test_util.test_logger("wait for 20 seconds to see if management node VM starts on any host")
    time.sleep(20)

    new_mn_host_ip = test_stub.get_host_by_consul_leader(test_lib.all_scenario_config, test_lib.scenario_file)
    if new_mn_host_ip == "":
        test_util.test_fail("management node VM not run correctly on [%s] after its former host [%s] down for 20s" % (new_mn_host_ip, mn_host_list[0].ip_))

    count = 60
    while count > 0:
        new_mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
        if len(new_mn_host) == 1:
            test_util.test_logger("management node VM run after its former host down for 30s")
            break
        elif len(new_mn_host) > 1:
            test_util.test_fail("management node VM runs on more than one host after its former host down")
        time.sleep(5)
        count -= 1

    if len(new_mn_host) == 0:
        test_util.test_fail("management node VM does not run after its former host down for 30s")
    elif len(new_mn_host) > 1:
        test_util.test_fail("management node VM runs on more than one host after its former host down")

    #node_ops.wait_for_management_server_start(300)
    test_stub.wrapper_of_wait_for_management_server_start(600)

    test_stub.ensure_hosts_connected(exclude_host=[mn_host_list[need_recover_mn_host_list[0]]])
    test_stub.ensure_bss_host_connected_from_stop(test_lib.scenario_file, test_lib.all_scenario_config, test_lib.deploy_config)
    test_stub.ensure_bss_connected()
    test_stub.ensure_pss_connected()

    test_stub.return_pass_ahead_if_3sites("TEST PASS") 

    vm = test_stub.create_basic_vm()

    vm.check()
    vm.destroy()

    test_util.test_pass('Create VM Test Success')

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
