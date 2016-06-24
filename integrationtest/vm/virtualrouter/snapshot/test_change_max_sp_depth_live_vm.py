'''

Will change incrementalSnapshot.maxNum to 4 and will create more than 16 
snapshots on same 1 snapshot. 

The sp tree will be like:
    sp1 -> sp2 -> sp3 -> sp4 -> sp5
    |       
    `-sp1.1 -> sp1.2 -> sp1.3 -> sp1.4 -> sp1.5
       |                    |
       |                    `-sp1.3.1->sp1.3.2-> ... ->sp1.3.5
       |                                   |
       |                                   `-sp1.3.2.1-..sp1.3.2.3 -> sp1.3.2.5
       |                                        |
       |                                        `-sp1.3.2.1.1...sp1.3.2.1.5
       |
       |
       `-sp1.1.1 -> sp1.1.2 -> ... -> sp1.1.5
            |
            `-sp1.1.1.1 ->sp1.1.1.2 -> ... -> sp1.1.1.5
                 |
                 `-sp1.1.1.1.1 ... sp1.1.1.1.5

The difference with snapshot/test_change_max_sp_depth.py is the snapshot ops
happens on running vm. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header

import os
import time

_config_ = {
        'timeout' : 9000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
default_snapshot_depth = None
test_depth = 4

def test():
    global default_snapshot_depth

    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)
    
    #this test will rely on live snapshot capability supporting
    host_inv = test_lib.lib_find_host_by_vm(vm1.get_vm())

    if not test_lib.lib_check_live_snapshot_cap(host_inv):
        vm1.destroy()
        test_obj_dict.rm_vm(vm1)
        test_util.test_skip('Skip test, since [host:] %s does not support live snapshot.')

    test_util.test_dsc('Create test vm as utility vm')
    default_snapshot_depth = conf_ops.change_global_config('volumeSnapshot', \
            'incrementalSnapshot.maxNum', test_depth)

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

    #volume doesn't need to be attached. It is because when create snapshot, 
    # the volume will be attached to utiltiy vm, who will add the volume.
    #snapshots = zstack_sp_header.ZstackVolumeSnapshot()
    #snapshots.set_target_volume(volume)
    #test_obj_dict.add_volume_snapshot(snapshots)
    snapshots = test_obj_dict.get_volume_snapshot(volume.get_volume().uuid)
    snapshots.set_utility_vm(vm)

    test_util.test_dsc('1. create 5 snapshots and check')
    num = 1
    while num < 6:
        snapshots.create_snapshot('sp %s' % str(num))
        num += 1

    snapshots.check()
    snapshot1 = snapshots.get_snapshot_head()
    snapshots.use_snapshot(snapshot1)

    test_util.test_dsc('1. create 5 new snapshots and check')
    num = 1
    while num < 6:
        snapshots.create_snapshot('sp 1.%s' % str(num))
        num += 1

    snapshots.check()
    snapshot1_3 = snapshots.get_current_snapshot().get_parent().get_parent()
    snapshot1_1 = snapshot1_3.get_parent().get_parent()

    snapshots.use_snapshot(snapshot1_3)
    test_util.test_dsc('1. create 5 new snapshots and check')
    num = 1
    while num < 6:
        snapshots.create_snapshot('sp 1.3.%s' % str(num))
        num += 1

    snapshots.check()
    snapshot1_3_2 = snapshots.get_current_snapshot().get_parent().get_parent().get_parent()

    snapshots.use_snapshot(snapshot1_3_2)
    test_util.test_dsc('1. create 5 new snapshots and check')
    num = 1
    while num < 6:
        snapshots.create_snapshot('sp 1.3.2.%s' % str(num))
        num += 1

    snapshots.check()
    snapshot1_3_2_1 = snapshots.get_current_snapshot().get_parent().get_parent().get_parent().get_parent()

    snapshots.use_snapshot(snapshot1_3_2_1)
    test_util.test_dsc('1. create 5 new snapshots and check')
    num = 1
    while num < 6:
        snapshots.create_snapshot('sp 1.3.2.1.%s' % str(num))
        num += 1

    snapshots.check()

    snapshots.use_snapshot(snapshot1_1)
    snapshots.create_snapshot('sp 1.1.1')
    snapshot1_1_1 = snapshots.get_current_snapshot()
    num = 2
    while num < 6:
        snapshots.create_snapshot('sp 1.1.%s' % str(num))
        num += 1

    snapshots.check()

    snapshots.use_snapshot(snapshot1_1_1)
    snapshots.create_snapshot('sp 1.1.1.1')
    snapshot1_1_1_1 = snapshots.get_current_snapshot()
    num = 2
    while num < 6:
        snapshots.create_snapshot('sp 1.1.1.%s' % str(num))
        num += 1

    snapshots.check()

    snapshots.use_snapshot(snapshot1_1_1_1)
    snapshots.create_snapshot('sp 1.1.1.1.1')
    snapshot1_1_1_1_1 = snapshots.get_current_snapshot()
    num = 2
    while num < 6:
        snapshots.create_snapshot('sp 1.1.1.1.%s' % str(num))
        num += 1

    snapshots.check()

    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    volume.check()
    volume.delete()

    test_obj_dict.rm_volume(volume)
    vm.destroy()
    conf_ops.change_global_config('volumeSnapshot', \
            'incrementalSnapshot.maxNum', default_snapshot_depth)
    test_util.test_pass('Create Snapshots with change max sp depth test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global default_snapshot_depth
    conf_ops.change_global_config('volumeSnapshot', \
            'incrementalSnapshot.maxNum', default_snapshot_depth)

    test_lib.lib_error_cleanup(test_obj_dict)
