'''

Integration Test for creating KVM VM in MN HA mode after stopping ha cluster.

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
    mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(mn_host) != 1:
        test_util.test_fail('MN VM is running on %d host(s)' % len(mn_host))
    test_util.test_logger("close MN-VM and all zs-ha services in cluster")
    test_stub.stop_zsha(mn_host[0], test_lib.all_scenario_config)
    new_mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(new_mn_host) != 0:
        test_util.test_fail('MN VM is still running after shutdown ha cluster')

    test_util.test_logger("start ha cluster")
    test_stub.start_zsha(mn_host[0], test_lib.all_scenario_config)
    test_util.test_logger("wait 50s for MN VM to start")
    time.sleep(50)
    mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(mn_host) != 1:
        test_util.test_fail('MN VM is running on %d host(s) after shutdown and start ha cluster' % len(mn_host))
    test_util.test_logger("wait for 5 minutes to see if management node starts again")
    #node_ops.wait_for_management_server_start(300)
    test_stub.wrapper_of_wait_for_management_server_start(600)
    test_util.test_pass('Shutdown HA Cluster Test Success')

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
