'''

Integration Test for creating KVM VM in MN HA mode with one mn host, which MN-VM is running on, network shutdown and recovery.

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
mn_host = None

def test():
    global vm
    global mn_host
    mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(mn_host) != 1:
        test_util.test_fail('MN VM is running on %d host(s)' % len(mn_host))
    test_util.test_logger("shutdown host's network [%s] that mn vm is running on" % (mn_host[0].ip_))
    test_stub.shutdown_host_network(mn_host[0], test_lib.all_scenario_config)
    test_util.test_logger("wait for 30 seconds to see if management node VM starts on another host")
    time.sleep(30)

    new_mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(new_mn_host) == 0:
        test_stub.recover_host(mn_host[0], test_lib.all_scenario_config, test_lib.deploy_config)
        test_util.test_fail("management node VM does not start after its former host down")
    elif len(new_mn_host) > 1:
        test_stub.recover_host(mn_host[0], test_lib.all_scenario_config, test_lib.deploy_config)
        test_util.test_fail("management node VM starts on more than one host after its former host down")
    try:
        node_ops.wait_for_management_server_start()
    except:
        test_stub.recover_host(mn_host[0], test_lib.all_scenario_config, test_lib.deploy_config)
        test_util.test_fail("management node does not recover after its former host's network down")

    test_util.test_logger("wait managemnet node for 10 seconds to connect to host")
    time.sleep(10)
    vm = test_stub.create_basic_vm()
    vm.check()
    vm.destroy()

    test_util.test_logger("recover host: %s" % (mn_host[0].ip_))
    test_stub.recover_host(mn_host[0], test_lib.all_scenario_config, test_lib.deploy_config)

    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
    test_util.test_logger("recover host: %s" % (mn_host[0].ip_))
    test_stub.recover_host(mn_host[0], test_lib.all_scenario_config, test_lib.deploy_config)
