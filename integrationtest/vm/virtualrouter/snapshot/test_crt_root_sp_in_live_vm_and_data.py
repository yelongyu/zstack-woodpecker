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

    live_snapshot = test_lib.lib_check_live_snapshot_cap(host_inv)
    if not live_snapshot:
        vm1.destroy()
        test_obj_dict.rm_vm(vm1)
        test_util.test_skip("Skip test, since [host:] %s doesn't support live snapshot " % host_inv.uuid)

    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)

    test_util.test_dsc('Create volume for snapshot testing')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name('volume for snapshot testing')
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume1 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume1)
    volume2 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume2)
    #make sure utility vm is starting and running
    vm.check()

    volume.attach(vm1)

    test_util.test_dsc('create snapshot for root')
    vm_root_volume_inv = test_lib.lib_get_root_volume(vm1.get_vm())
    snapshots = test_obj_dict.get_volume_snapshot(vm_root_volume_inv.uuid)
    snapshots.set_utility_vm(vm)
    snapshots.create_snapshot('create_root_volume_snapshot1')
    volume1.check()
    volume2.check()

    snapshots2 = test_obj_dict.get_volume_snapshot(volume1.get_volume().uuid)
    snapshots2.set_utility_vm(vm)
    snapshots2.create_snapshot('create_data_volume_snapshot1')
    snapshots.check()
    volume1.check()
    volume2.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create root Snapshot and test data volume status test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
