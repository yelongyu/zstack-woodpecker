'''

New Integration test for testing vm migration when doing host maintenance in Local storage.

Test steps:

1. Create 2 VMs and 1 volume.
2. Attach 1 volume to vm1
3. migrate 2 VMs to random target_host
4. change target_host state to maintain. All vms will be stopped.
5. check 2 VMs and volume status
6. Enable maintained host again.
7. Migrate 2 stoped VMs volume to new target_host
8. Check 2 VMs and volume status again.

This case should not be parallely executed with other test case, since it will
impact other vm state in test db.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.header.vm as vm_header
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
host = None

def is_host_connected(host_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host = res_ops.query_resource(res_ops.HOST, cond)[0]
    if host.status == 'Connected':
        return True

def test():
    global host
    if test_lib.lib_get_active_host_number() < 2:
        test_util.test_fail('Not available host to do maintenance, since there are not 2 hosts')

    vm1 = test_stub.create_vm(vm_name = 'maintain_host_vm1')
    test_obj_dict.add_vm(vm1)

    vm2 = test_stub.create_vm(vm_name = 'maintain_host_vm2')
    test_obj_dict.add_vm(vm2)

    vm1.check()
    vm2.check()

    test_util.test_dsc('Create volume and check')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)

    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)

    test_util.test_dsc('Attach volume and check')
    volume.attach(vm1)
    volume.check()

    current_host1 = test_lib.lib_get_vm_host(vm1.vm)
    conditions = res_ops.gen_query_conditions('state', '=', host_header.ENABLED)
    conditions = res_ops.gen_query_conditions('status', '=', host_header.CONNECTED, conditions)
    all_hosts = res_ops.query_resource(res_ops.HOST, conditions)

    target_host = random.choice(all_hosts)
    if current_host1.uuid != target_host.uuid:
        vm1.migrate(target_host.uuid)

    current_host2 = test_lib.lib_get_vm_host(vm2.vm)
    if current_host2.uuid != target_host.uuid:
        vm2.migrate(target_host.uuid)

    new_host = test_lib.lib_get_vm_host(vm1.vm)
    if new_host.uuid != target_host.uuid:
        test_util.test_fail('VM did not migrate to target [host:] %s, but to [host:] %s' % (target_host.uuid, new_host.uuid))

    volume.check()

    host = test_kvm_host.ZstackTestKvmHost()
    host.set_host(target_host)

    host.maintain()

    #need to update vm's inventory, since they will be changed by maintenace mode
    vm1.update()
    vm2.update()
    vm1.set_state(vm_header.STOPPED)
    vm2.set_state(vm_header.STOPPED)

    vm1.check()
    vm2.check()
    volume.check()

    host.change_state(test_kvm_host.ENABLE_EVENT)
    if not linux.wait_callback_success(is_host_connected, host.get_host().uuid, 120):
        test_util.test_fail('host status is not changed to connected, after changing its state to Enable')

    volume.detach()

    vm1_root_volume = test_lib.lib_get_root_volume(vm1.get_vm())
    vm2_root_volume = test_lib.lib_get_root_volume(vm2.get_vm())

    conditions = res_ops.gen_query_conditions('uuid', '!=', target_host.uuid, conditions)
    rest_hosts = res_ops.query_resource(res_ops.HOST, conditions)
    new_target_host = random.choice(rest_hosts)

    vol_ops.migrate_volume(vm1_root_volume.uuid, new_target_host.uuid)
    vol_ops.migrate_volume(vm2_root_volume.uuid, new_target_host.uuid)
    vol_ops.migrate_volume(volume.get_volume().uuid, new_target_host.uuid)

    volume.attach(vm1)

    vm1.start()
    vm2.start()

    vm1.check()
    vm2.check()
    volume.check()

    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    volume.delete()
    test_obj_dict.rm_volume(volume)
    test_util.test_pass('Maintain Host Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if host:
        host.change_state(test_kvm_host.ENABLE_EVENT)
