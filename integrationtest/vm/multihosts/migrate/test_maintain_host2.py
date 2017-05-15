'''

New Integration test for testing vm migration when doing host maintenance

Test steps:

1. Create 2 VMs.
3. migrate 2 VMs to random target_host
4. change target_host state to maintain
5. check 2 VMs
6. Enable maintained host again.
7. Migrate 2 VMs back to target_host
8. Check 2 VMs status again.

This case should not be parallely executed with other test case, since it will
impact other vm state in test db.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_kvm_host as test_kvm_host
import zstackwoodpecker.header.host as host_header
import apibinding.inventory as inventory
import zstacklib.utils.linux as linux
import time
import os
import random

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def is_host_connected(host_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host = res_ops.query_resource(res_ops.HOST, cond)[0]
    if host.status == 'Connected':
        return True

def test():
    vm1 = test_stub.create_vr_vm('maintain_host_vm1', 'imageName_s', 'l3VlanNetwork2')
    test_obj_dict.add_vm(vm1)

    vm2 = test_stub.create_vr_vm('maintain_host_vm2', 'imageName_s', 'l3VlanNetwork2')
    test_obj_dict.add_vm(vm2)

    vm1.check()
    vm2.check()
    if not test_lib.lib_check_vm_live_migration_cap(vm1.vm) or not test_lib.lib_check_vm_live_migration_cap(vm2.vm):
        test_util.test_skip('skip migrate if live migrate not supported')

    current_host1 = test_lib.lib_get_vm_host(vm1.vm)
    conditions = res_ops.gen_query_conditions('clusterUuid', '=', vm1.vm.clusterUuid)
    conditions = res_ops.gen_query_conditions('state', '=', host_header.ENABLED, conditions)
    conditions = res_ops.gen_query_conditions('status', '=', host_header.CONNECTED, conditions)
    all_hosts = res_ops.query_resource(res_ops.HOST, conditions)
    if len(all_hosts) <= 1:
        test_util.test_fail('Not available host to do maintenance, since there is only %s host' % len(all_hosts))

    target_host = random.choice(all_hosts)
    if current_host1.uuid != target_host.uuid:
        vm1.migrate(target_host.uuid)

    current_host2 = test_lib.lib_get_vm_host(vm2.vm)
    if current_host2.uuid != target_host.uuid:
        vm2.migrate(target_host.uuid)

    new_host = test_lib.lib_get_vm_host(vm1.vm)
    if new_host.uuid != target_host.uuid:
        test_util.test_fail('VM did not migrate to target [host:] %s, but to [host:] %s' % (target_host.uuid, new_host.uuid))

    host = test_kvm_host.ZstackTestKvmHost()
    host.set_host(target_host)

    host.maintain()

    #need to update vm's inventory, since they will be changed by maintenace mode
    vm1.update()
    vm2.update()

    vm1.check()
    vm2.check()

    host.change_state(test_kvm_host.ENABLE_EVENT)
    if not linux.wait_callback_success(is_host_connected, host.get_host().uuid, 120):
        test_util.test_fail('host status is not changed to connected, after changing its state to Enable')

    vm1.migrate(target_host.uuid)
    vm2.migrate(target_host.uuid)

    vm1.check()
    vm2.check()

    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    test_util.test_pass('Maintain Host Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
