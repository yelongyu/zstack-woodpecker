'''

Integration Test for creating KVM VM in MN HA mode with one mn host, which MN-VM is running on, shutdown and recovery.

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
    mn_ip = os.environ.get('zstackHaVip')
    mn_host = test_stub.get_host_by_mn_vm(mn_ip,test_lib.all_scenario_config, test_lib.scenario_file)
    if len(mn_host) != 1:
        test_util.test_fail('MN VM is running on %d host(s)' % len(mn_host))
    test_util.test_logger("shutdown host [%s] that mn vm is running on" % (mn_host[0].ip_))
    test_stub.stop_host(mn_host[0], test_lib.all_scenario_config)
    test_util.test_logger("wait for 2 minutes to see if management node starts again")
    try:
        node_ops.warit_for_management_server_start()
    except:
        test_util.test_fail("management node does not recover after its former host down")

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
