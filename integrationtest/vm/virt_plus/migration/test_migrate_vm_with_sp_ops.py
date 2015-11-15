'''

Test create/restore snapshot functions with vm migration. 

@author: Youyk
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
    vm = test_stub.create_vm(vm_name = 'migrate_vm_with_snapshot')
    test_obj_dict.add_vm(vm)

    test_util.test_dsc('Create volume for snapshot testing')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name('volume for snapshot testing')
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    #make sure utility vm is starting and running
    vm.check()

    volume.attach(vm)
    volume.detach()

    test_util.test_dsc('create snapshot and check')
    snapshots = test_obj_dict.get_volume_snapshot(volume.get_volume().uuid)
    snapshots.set_utility_vm(vm)
    snapshots.create_snapshot('create_snapshot1')
    snapshots.check()

    #if not attach volume, vm migration won't migrate data volume
    volume.attach(vm)
    test_util.test_dsc('migrate vm and check snapshot')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    volume.detach()
    snapshots.check()

    snapshot1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot2')
    snapshots.check()
    snapshots.create_snapshot('create_snapshot3')
    snapshots.check()
    snapshot3 = snapshots.get_current_snapshot()

    snapshots.use_snapshot(snapshot1)
    snapshots.create_snapshot('create_snapshot1.1.1')
    snapshots.check()
    snapshots.create_snapshot('create_snapshot1.1.2')
    snapshots.check()

    snapshots.use_snapshot(snapshot1)
    snapshots.create_snapshot('create_snapshot1.2.1')
    snapshots.check()
    snapshot1_2_1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot1.2.2')
    snapshots.check()

    volume.attach(vm)
    test_util.test_dsc('migrate vm and check snapshot')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    volume.detach()
    snapshots.check()

    snapshots.use_snapshot(snapshot3)
    snapshots.check()
    snapshots.create_snapshot('create_snapshot4')
    snapshots.check()

    volume.attach(vm)
    test_util.test_dsc('migrate vm and check snapshot')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    volume.detach()
    snapshots.check()

    test_util.test_dsc('Delete snapshot, volume and check')
    snapshots.delete_snapshot(snapshot3)
    snapshots.check()

    volume.attach(vm)
    test_util.test_dsc('migrate vm and check snapshot')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    volume.detach()
    snapshots.check()

    snapshots.delete_snapshot(snapshot1_2_1)
    snapshots.check()

    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    volume.check()
    volume.delete()

    test_obj_dict.rm_volume(volume)
    vm.destroy()
    test_util.test_pass('Create Snapshot with VM migration test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
