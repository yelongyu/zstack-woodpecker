'''

Test remove all snapshots. 

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
    #make sure utility vm is starting and running
    vm.check()

    test_util.test_dsc('create snapshot and delete it')
    #snapshots = zstack_sp_header.ZstackVolumeSnapshot()
    #snapshots.set_target_volume(volume)
    #test_obj_dict.add_volume_snapshot(snapshots)
    snapshots = test_obj_dict.get_volume_snapshot(volume.get_volume().uuid)
    snapshots.set_utility_vm(vm)
    snapshots.create_snapshot('create_snapshot1')
    snapshot1 = snapshots.get_current_snapshot()
    snapshots.delete_snapshot(snapshot1)

    test_util.test_dsc('create 2 new snapshots, then delete the 1st one')
    snapshots.create_snapshot('create_snapshot2')
    snapshot2 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot3')
    snapshot3 = snapshots.get_current_snapshot()
    snapshots.check()
    snapshots.delete_snapshot(snapshot2)

    test_util.test_dsc('create new snapshot to backup')
    snapshots.create_snapshot('create_snapshot4')
    snapshot4 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot5')
    #snapshot4.backup()
    #snapshots.check()

    #test_util.test_dsc('use new backuped snapshot4 and delete it later. ')
    snapshots.use_snapshot(snapshot4)
    snapshots.check()
    snapshots.delete_snapshot(snapshot4)

    test_util.test_dsc('try to create last snapshot and delete it. ')
    snapshots.create_snapshot('create_snapshot6')
    snapshots.check()
    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    
    volume.check()
    test_obj_dict.rm_volume(volume)
    vm.check()

    vm.destroy()
    test_util.test_pass('Cleanup all Snapshots test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
