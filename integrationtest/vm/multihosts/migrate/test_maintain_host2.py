'''

New Integration test for testing vm migration when doing host maintenance

Test steps:

1. Create 2 VMs.
3. migrate 2 VMs to random target_host
4. change target_host state to maintain
5. check 2 VMs
6. Enable maintained host again.
7. Migrate 2 VMs back to original_host
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
import zstackwoodpecker.header.vm as vm_header
import time
import os
import random

_config_ = {
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def is_host_connected(host_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host = res_ops.query_resource(res_ops.HOST, cond)[0]
    if host.status == 'Connected' and host.state == 'Enabled':
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
    current_host2 = test_lib.lib_get_vm_host(vm2.vm)
    conditions = res_ops.gen_query_conditions('clusterUuid', '=', vm1.vm.clusterUuid)
    conditions = res_ops.gen_query_conditions('state', '=', host_header.ENABLED, conditions)
    conditions = res_ops.gen_query_conditions('status', '=', host_header.CONNECTED, conditions)
    all_hosts = res_ops.query_resource(res_ops.HOST, conditions)
    if len(all_hosts) <= 1:
        test_util.test_fail('Not available host to do maintenance, since there is only %s host' % len(all_hosts))
    vr = test_lib.lib_get_all_vrs()
    if len(vr) == 0:
        test_util.test_skip('Skip test if not using vr')
    vr_uuid = vr[0].uuid
    vr_host_uuid = test_lib.lib_get_vm_host(vr[0]).uuid

    for host_n in all_hosts:
        print'host_n%s'% (host_n.uuid)
        if host_n.uuid != current_host1.uuid:
            if host_n.uuid != current_host2.uuid:
                if host_n.uuid != vr_host_uuid:
                    target_host = host_n
                    print'target_host_uuid%s'%(target_host.uuid)
                    vm1.migrate(target_host.uuid)
                    vm2.migrate(target_host.uuid)
                    break   
    else:
        test_util.test_skip('can not find a host to migrate two host')
    new_host = test_lib.lib_get_vm_host(vm1.vm)
    if new_host.uuid != target_host.uuid:
        test_util.test_fail('VM did not migrate to target [host:] %s, but to [host:] %s' % (target_host.uuid, new_host.uuid))

    new_host1 = test_lib.lib_get_vm_host(vm2.vm)
    if new_host1.uuid != target_host.uuid:
        test_util.test_fail('VM did not migrate to target [host:] %s, but to [host:] %s' % (target_host.uuid, new_host1.uuid))

    host = test_kvm_host.ZstackTestKvmHost()
    host.set_host(target_host)
    host.maintain()
    #need to update vm's inventory, since they will be changed by maintenace mode
    vm1.update()
    vm2.update()

    ps = test_lib.lib_get_primary_storage_by_vm(vm1.get_vm())
    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        vm1.set_state(vm_header.STOPPED)
        vm2.set_state(vm_header.STOPPED)
    vm1.check()
    vm2.check()
    host.change_state(test_kvm_host.ENABLE_EVENT)
    if not linux.wait_callback_success(is_host_connected, host.get_host().uuid, 120):
        test_util.test_fail('host status is not changed to connected or host state is not changed to Enabled within 120s')

    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        vm1.start()
        vm2.start()

    vm1.set_state(vm_header.RUNNING)
    vm2.set_state(vm_header.RUNNING)
    vm1.check()
    vm2.check()
    
    post_host1 = test_lib.lib_get_vm_host(vm1.vm)
    post_host2 = test_lib.lib_get_vm_host(vm2.vm)

    if post_host1.uuid != current_host1.uuid:
        vm1.migrate(current_host1.uuid)

    if post_host2.uuid != current_host2.uuid:
        vm2.migrate(current_host2.uuid)

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
