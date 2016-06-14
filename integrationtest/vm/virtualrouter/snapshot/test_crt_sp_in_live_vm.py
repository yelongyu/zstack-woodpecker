'''

Test create/restore snapshot functions, which will be happed on a running VM. 

This test is to simulate user save/restore snapshot on a real running VM. 
The test will be skipped, if host doesn't support live snapshot operations.

When delete a snapshot in the middle of snapshot chain, libvirt will merge
the rest snapshots to base. The operation is only valid to living vm, only if 
libvirt version is larger than 1.2.7 . If libvirt is less than 1.2.7, it needs
to stop VM, before delete snapshot. It will be covered in 
test_crt_sp_in_live_vm.py2

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
from distutils.version import StrictVersion

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm as utility vm')
    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)
    #this test will rely on live snapshot capability supporting
    host_inv = test_lib.lib_find_host_by_vm(vm1.get_vm())

    if not test_lib.lib_check_live_snapshot_cap(host_inv):
        vm1.destroy()
        test_obj_dict.rm_vm(vm1)
        test_util.test_skip('Skip test, since [host:] %s does not support live snapshot.' % host_inv.uuid)

    libvirt_ver = test_lib.lib_get_host_libvirt_tag(host_inv)
    if not libvirt_ver or StrictVersion(libvirt_ver) < StrictVersion('1.2.7'):
        vm1.destroy()
        test_obj_dict.rm_vm(vm1)
        test_util.test_skip("Skip test, since [host:] %s libvert version: %s is lower than 1.2.7, which doesn't support live merge, when doing snapshot deleting." % (host_inv.uuid, libvirt_ver))

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

    volume.attach(vm1)

    test_util.test_dsc('create snapshot and check')
    #snapshots = zstack_sp_header.ZstackVolumeSnapshot()
    #snapshots.set_target_volume(volume)
    #test_obj_dict.add_volume_snapshot(snapshots)
    snapshots = test_obj_dict.get_volume_snapshot(volume.get_volume().uuid)
    snapshots.set_utility_vm(vm)
    snapshots.create_snapshot('create_snapshot1')
    snapshots.check()

    snapshot1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot2')
    snapshots.check()
    snapshots.create_snapshot('create_snapshot3')
    snapshots.check()
    snapshot3 = snapshots.get_current_snapshot()

    #even with live snapshot function, the revert need stop vm.
    vm1.stop()    
    snapshots.use_snapshot(snapshot1)
    vm1.start()
    snapshots.create_snapshot('create_snapshot1.1.1')
    snapshots.check()
    snapshots.create_snapshot('create_snapshot1.1.2')
    snapshots.check()

    vm1.stop()
    snapshots.use_snapshot(snapshot1)
    vm1.start()
    snapshots.create_snapshot('create_snapshot1.2.1')
    snapshots.check()
    snapshot1_2_1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot1.2.2')
    snapshots.check()

    vm1.stop()
    snapshots.use_snapshot(snapshot3)
    snapshots.check()
    snapshots.create_snapshot('create_snapshot4')
    snapshots.check()
    #delay start vm
    vm1.start()

    test_util.test_dsc('Delete snapshot, volume and check')
    snapshots.delete_snapshot(snapshot3)
    snapshots.check()

    snapshots.delete_snapshot(snapshot1_2_1)
    snapshots.check()

    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    volume.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create Snapshot test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
