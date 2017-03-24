'''

Integration Test for creating KVM VM in MN HA mode after migrating mn vm to another mn host.

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

def test():
    global vm
    ori_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
    if len(ori_host) != 1:
        test_util.test_fail('MN VM is running on %d host(s)' % len(ori_host))
    mn_host_list = test_stub.get_mn_host(test_lib.all_scenario_config, test_lib.scenario_file)
    ori_host = ori_host[0]
    target_host = None
    for host in mn_host_list:
        if host.ip_ != ori_host.ip_:
            target_host = host
            break
    if target_host:
        test_stub.migrate_mn_vm(target_host, test_lib.all_scenario_config)
        cur_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
        if len(cur_host) != 1:
            test_util.test_fail('MN VM is running on %d host(s)' % len(cur_host))
        cur_host = cur_host[0]
        if cur_host.ip_ != target_host.ip_:
            test_util.test_fail("mn vm should be migrated to host[ %s ], but it was migrated to host[ %s ]" % (target_host.ip_, cur_host.ip_))
        else:
            vm = test_stub.create_basic_vm()
            vm.check()
            vm.destroy()
            test_util.test_pass('Migrate MN VM Test Success')        
    else:
        test_util.test_fail("there is no host for mn vm to migrate to")

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
