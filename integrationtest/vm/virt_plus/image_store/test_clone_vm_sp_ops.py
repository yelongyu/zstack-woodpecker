'''

New Integration Test for cloning KVM VM with snapshot operations.

@author: Youyk
'''
import time
import os

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vn_prefix = 'vm-clone-%s' % time.time()
vm_name1 = ['%s-vm1']

def test():
    vm = test_stub.create_vm(vm_name = vn_prefix)
    test_obj_dict.add_vm(vm)
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    for bs in backup_storage_list:
        if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            break
    else:
        vm.destroy()
        test_util.test_skip('Not find image store type backup storage.')

    vm1 = test_stub.create_vm(vm_name = vn_prefix)
    test_obj_dict.add_vm(vm1)
    vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
    test_util.test_dsc('create snapshot and check')
    snapshots = test_obj_dict.get_volume_snapshot(vm_root_volume_inv.uuid)
    snapshots.set_utility_vm(vm1)
    snapshots.create_snapshot('create_root_snapshot1')
    snapshot1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_root_snapshot2')

    snapshots.delete_snapshot(snapshot1)
    vm.reboot()
    new_vm1 = vm.clone(vm_name1)[0]
    test_obj_dict.add_vm(new_vm1)
    vm.destroy()

    new_vm1.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Clone VM Test with snapshot operations Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
