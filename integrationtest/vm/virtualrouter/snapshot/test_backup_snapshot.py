'''

Test backup snapshot to backup storage. Then delete volumes, which will delete 
all snapshots on primary storage. Then we will use backup snapshot to create
new volume and doing test. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
import apibinding.inventory as inventory

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm as utility vm')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)

    test_util.test_dsc('Create volume for snapshot testing')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name('volume for snapshot testing')
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.attach(vm)
    import time
    time.sleep(10)
    volume.detach()
    ps_uuid = volume.get_volume().primaryStorageUuid
    ps = test_lib.lib_get_primary_storage_by_uuid(ps_uuid)
    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        # LOCAL Storage do not support create volume and template from backuped snapshot
        test_lib.lib_robot_cleanup(test_obj_dict)
        test_util.test_skip('Skip test create volume from backuped storage, when volume is deleted.')

    #make sure utility vm is starting and running
    vm.check()

    test_util.test_dsc('create snapshot and check')
    snapshots = test_obj_dict.get_volume_snapshot(volume.get_volume().uuid)
    snapshots.set_utility_vm(vm)
    snapshots.create_snapshot('create_snapshot1')
    snapshot1 = snapshots.get_current_snapshot()
    snapshot1.backup()
    original_checking_points1 = snapshots.get_checking_points(snapshot1)
    snapshots.create_snapshot('create_snapshot2')
    snapshots.create_snapshot('create_snapshot3')
    snapshot3 = snapshots.get_current_snapshot()
    snapshot3.backup()
    original_checking_points3 = snapshots.get_checking_points(snapshot3)

    volume.delete()

    test_util.test_dsc('create new data volume based on backuped snapshot1')
    volume1 = snapshot1.create_data_volume(name = 'snapshot1_volume')
    test_obj_dict.add_volume(volume1)
    volume1.attach(vm)
    volume1.check()
    volume1.detach()

    snapshots1 = test_obj_dict.get_volume_snapshot(volume1.get_volume().uuid)
    snapshots1.set_utility_vm(vm)

    test_util.test_dsc('create new data volume based on backuped snapshot3')
    volume3 = snapshot3.create_data_volume(name = 'snapshot3_volume')
    test_obj_dict.add_volume(volume3)
    #create data volume from sp doesn't need a pre-attach/detach
    volume3.check()

    snapshots3 = test_obj_dict.get_volume_snapshot(volume3.get_volume().uuid)
    snapshots3.set_utility_vm(vm)

    snapshots1.create_snapshot('create_snapshot1-1')
    snapshots1.check()

    snapshots3.create_snapshot('create_snapshot3-1')
    snapshots3.create_snapshot('create_snapshot3-2')
    snapshots.delete_snapshot(snapshot3)
    snapshots3.check()

    test_util.test_dsc('Delete snapshot, volume and check')
    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    snapshots1.check()
    snapshots1.delete()
    test_obj_dict.rm_volume_snapshot(snapshots1)
    snapshots3.check()
    snapshots3.delete()
    test_obj_dict.rm_volume_snapshot(snapshots3)

    volume.delete()
    test_obj_dict.rm_volume(volume)
    vm.destroy()
    test_util.test_pass('Backup Snapshot test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
