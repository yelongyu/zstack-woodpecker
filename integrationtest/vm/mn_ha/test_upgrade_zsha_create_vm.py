'''

Integration Test for creating KVM VM in MN HA mode after upgrade zsha.

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

def test():
    mn_vm_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)

    if not test_stub.upgrade_zsha(test_lib.all_scenario_config, test_lib.scenario_file):
        test_util.test_fail('Fail to upgrade zsha')
    if len(mn_vm_host) != 1:
        test_util.test_fail('MN VM is running on %d host(s)' % len(mn_vm_host))

    test_util.test_logger('wait for 10s to see if something happens')
    time.sleep(10)

    try:
        new_mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
        if len(new_mn_host) == 0:
            test_util.test_fail("management node VM was destroyed after upgrade zsha")
        elif len(new_mn_host) > 1:
            test_util.test_fail("management node VM starts on more than one host after upgrade zsha")
    except:
        test_util.test_fail("management node VM was destroyed after upgrade zsha")
    if new_mn_host[0].ip_ != mn_vm_host[0].ip_:
        test_util.test_fail('management node VM starts on another host after upgrade zsha')

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
    pass

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
