'''

Test create/restore snapshot functions with vm migration. 

@author: Glody 
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm as utility vm')
    vm = test_stub.create_vr_vm('migrate_vm_with_snapshot', 'imageName_net', 'l3VlanNetwork2')
    test_obj_dict.add_vm(vm)
    vm.check()

    root_volume_uuid = test_lib.lib_get_root_volume_uuid(vm.get_vm())
    test_util.test_dsc('create snapshot and check')
    snapshots = test_obj_dict.get_volume_snapshot(root_volume_uuid)
    snapshots.set_utility_vm(vm)
    snapshots.create_snapshot('create_snapshot1')
    snapshots.check()

    test_util.test_dsc('migrate vm and check snapshot')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    snapshots.check()

    snapshot1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot2')
    snapshots.check()
    snapshots.create_snapshot('create_snapshot3')
    snapshots.check()
    snapshot3 = snapshots.get_current_snapshot()

    vm.stop()
    snapshots.use_snapshot(snapshot1)
    vm.start()

    snapshots.create_snapshot('create_snapshot1.1.1')
    snapshots.check()
    snapshots.create_snapshot('create_snapshot1.1.2')
    snapshots.check()

    vm.stop()
    snapshots.use_snapshot(snapshot1)
    vm.start()

    snapshots.create_snapshot('create_snapshot1.2.1')
    snapshots.check()
    snapshot1_2_1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot1.2.2')
    snapshots.check()

    test_util.test_dsc('migrate vm and check snapshot')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    snapshots.check()

    vm.stop()
    snapshots.use_snapshot(snapshot3)
    vm.start()

    snapshots.check()
    snapshots.create_snapshot('create_snapshot4')
    snapshots.check()

    test_util.test_dsc('migrate vm and check snapshot')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    snapshots.check()

    test_util.test_dsc('Delete snapshot and check')
    snapshots.delete_snapshot(snapshot3)
    snapshots.check()

    test_util.test_dsc('migrate vm and check snapshot')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    snapshots.check()

    snapshots.delete_snapshot(snapshot1_2_1)
    snapshots.check()

    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)

    vm.destroy()
    test_util.test_pass('Create Snapshot with VM migration test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
