'''

Test create/restore 100 snapshots functions. In this test, the snapshot was 
created on unattached data volume. 

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
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)

    test_util.test_dsc('Create volume for snapshot testing')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name('volume for snapshot testing')
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    vm.check()

    #snapshots = zstack_sp_header.ZstackVolumeSnapshot()
    #snapshots.set_target_volume(volume)
    #test_obj_dict.add_volume_snapshot(snapshots)
    snapshots = test_obj_dict.get_volume_snapshot(volume.get_volume().uuid)
    snapshots.set_utility_vm(vm)

    test_util.test_dsc('1. create 15 snapshots and check')
    num = 1
    while num < 16:
        snapshots.create_snapshot('create_snapshot%s' % str(num))
        num += 1

    snapshots.check()
    #16 is a special num for create snapshot base
    snapshot15 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot16')
    snapshot16 = snapshots.get_current_snapshot()
    snapshots.check()
    snapshots.create_snapshot('create_snapshot17')
    snapshot17 = snapshots.get_current_snapshot()
    snapshots.check()

    test_util.test_dsc('2. create 16 snapshots based on snapshot 15 and check')
    snapshots.use_snapshot(snapshot15)
    num = 1
    while num < 17:
        snapshots.create_snapshot('create_snapshot15.%s' % str(num))
        num += 1

    snapshots.check()

    test_util.test_dsc('3. create 16 snapshots based on snapshot 16 and check')
    snapshots.use_snapshot(snapshot16)
    num = 1
    while num < 17:
        snapshots.create_snapshot('create_snapshot16.%s' % str(num))
        num += 1

    snapshots.check()

    test_util.test_dsc('4. create 16 snapshots based on snapshot 17 and check')
    snapshots.use_snapshot(snapshot17)
    num = 18
    while num < (18 + 17):
        snapshots.create_snapshot('create_snapshot%s' % str(num))
        num += 1

    snapshots.check()

    #detele snapshot17
    test_util.test_dsc('5. delete snapshot 17 and create another 16 snapshots')
    snapshots.delete_snapshot(snapshot17)

    num = 35
    while num < (35 + 17):
        snapshots.create_snapshot('create_snapshot%s' % str(num))
        num += 1

    snapshots.check()

    #use snapshot16
    test_util.test_dsc('6. revert snapshot 16 and create another 16 snapshots')
    snapshots.use_snapshot(snapshot16)

    num = 1
    while num < 17:
        snapshots.create_snapshot('create_snapshot16.%s' % str(num))
        num += 1

    snapshots.check()

    #detele snapshot15
    test_util.test_dsc('7. use snapshot15, delete snapshot 15 and create another 16 snapshots')
    snapshots.use_snapshot(snapshot15)
    snapshots.delete_snapshot(snapshot15)

    num = 1
    while num < 17:
        snapshots.create_snapshot('create_snapshot15_2.%s' % str(num))
        num += 1

    snapshots.check()
    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    volume.check()
    volume.delete()

    test_obj_dict.rm_volume(volume)
    vm.destroy()
    test_util.test_pass('Create 100 Snapshots test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
