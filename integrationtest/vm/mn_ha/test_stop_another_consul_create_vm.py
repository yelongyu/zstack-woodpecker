'''

Integration Test for creating KVM VM in MN HA mode after stopping consul on another host.

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
test_host = None

def test():
    global vm
    global test_host
    mn_vm_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(mn_vm_host) != 1:
        test_util.test_fail('MN VM is running on %d host(s)' % len(mn_vm_host))
    mn_host_list = test_stub.get_mn_host(test_lib.all_scenario_config, test_lib.scenario_file)
    for mn_host in mn_host_list:
        if mn_host.ip_ != mn_vm_host[0].ip_:
            test_host = mn_host
            break
    if not test_host:
        test_util.test_fail('there is only one mn host')

    test_util.test_logger("stop consul for host [%s] that mn vm is running on" % (test_host.ip_))
    test_stub.stop_consul(test_host, test_lib.all_scenario_config)
    test_util.test_logger("wait for 20 seconds to see if management node VM starts on another host")
    time.sleep(20)
    try:
        new_mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
        if len(new_mn_host) == 0:
            test_util.test_fail("management node VM was destroyed after stopping another host's consul")
        elif len(new_mn_host) > 1:
            test_util.test_fail("management node VM starts on more than one host after stopping another host's consul")
    except:
        test_util.test_fail("management node VM was destroyed after stopping another host's consul")
    if new_mn_host[0].ip_ != mn_vm_host[0].ip_:
        test_util.test_fail('management node VM starts on another host when another host stopped consul')

    test_stub.ensure_hosts_connected()
    test_stub.ensure_pss_connected()
    test_stub.ensure_bss_host_connected_from_stop(test_lib.scenario_file, test_lib.all_scenario_config, test_lib.deploy_config)
    test_stub.ensure_bss_connected()

    test_stub.return_pass_ahead_if_3sites("TEST PASS")
    vm = test_stub.create_basic_vm()
    vm.check()
    vm.destroy()

    test_util.test_pass('Create VM Test Success')

#Will be called what ever test result is
def env_recover():
    test_util.test_logger("recover consul on host: %s" % (test_host.ip_))
    test_stub.start_consul(test_host, test_lib.all_scenario_config)
    test_stub.wait_for_mn_ha_ready(test_lib.all_scenario_config, test_lib.scenario_file)

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
