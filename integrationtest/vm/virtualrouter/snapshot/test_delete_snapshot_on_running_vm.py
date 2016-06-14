'''

Delete snapshot on running vm.
The test will be skipped, if host doesn't support live snapshot operations.

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
    #this test will rely on live snapshot capability supporting
    host_inv = test_lib.lib_find_host_by_vm(vm.get_vm())

    if not test_lib.lib_check_live_snapshot_cap(host_inv):
        vm.destroy()
        test_obj_dict.rm_vm(vm)
        test_util.test_skip('Skip test, since [host:] %s does not support live snapshot.')

    #libvirt_ver = test_lib.lib_get_host_libvirt_tag(host_inv)
    #if not libvirt_ver or libvirt_ver < '1.2.7':
    #    vm.destroy()
    #    test_obj_dict.rm_vm(vm)
    #    test_util.test_skip("Skip test, since [host:] %s libvert version: %s is lower than 1.2.7, which doesn't support live merge, when doing snapshot deleting." % (host_inv.uuid, libvirt_ver))

    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)

    test_util.test_dsc('Create volume for snapshot testing')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name('volume for snapshot testing')
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    #make sure utility vm is starting and running
    vm.check()

    test_util.test_dsc('create snapshot and check')
    #snapshots = zstack_sp_header.ZstackVolumeSnapshot()
    #snapshots.set_target_volume(volume)
    #test_obj_dict.add_volume_snapshot(snapshots)
    snapshots = test_obj_dict.get_volume_snapshot(volume.get_volume().uuid)
    snapshots.set_utility_vm(vm)
    snapshots.create_snapshot('create_snapshot1')
    snapshots.create_snapshot('create_snapshot2')
    snapshots.create_snapshot('create_snapshot3')

    volume.attach(vm1)
    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    volume.check()
    vm.destroy()
    test_obj_dict.rm_vm(vm)

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Delete Snapshot on running vm test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
