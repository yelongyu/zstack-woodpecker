'''

Test create/restore snapshot functions for windows, which will be happed on a running VM. 

This test is to simulate user save/restore snapshot on a real running VM with windows platform. 
The test will be skipped, if host doesn't support live snapshot operations.

When delete a snapshot in the middle of snapshot chain, libvirt will merge
the rest snapshots to base. The operation is only valid to living vm, only if 
libvirt version is larger than 1.2.7 . 

@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
from distutils.version import LooseVersion

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm as utility vm')
    new_offering = test_lib.lib_create_instance_offering(cpuNum = 6, memorySize = 2048 * 1024 * 1024)
    new_offering_uuid = new_offering.uuid
    vm1 = test_stub.create_windows_vm_2(instance_offering_uuid = new_offering_uuid)
    test_obj_dict.add_vm(vm1)
    #this test will rely on live snapshot capability supporting
    host_inv = test_lib.lib_find_host_by_vm(vm1.get_vm())

    if not test_lib.lib_check_live_snapshot_cap(host_inv):
        vm1.destroy()
        test_obj_dict.rm_vm(vm1)
        test_util.test_skip('Skip test, since [host:] %s does not support live snapshot.' % host_inv.uuid)

    libvirt_ver = test_lib.lib_get_host_libvirt_tag(host_inv)
    if not libvirt_ver or LooseVersion(libvirt_ver) < LooseVersion('1.2.7'):
        vm1.destroy()
        test_obj_dict.rm_vm(vm1)
        test_util.test_skip("Skip test, since [host:] %s libvert version: %s is lower than 1.2.7, which doesn't support live merge, when doing snapshot deleting." % (host_inv.uuid, libvirt_ver))

    test_util.test_dsc('Create volume for snapshot testing')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name('volume for snapshot testing')
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    #make sure utility vm is starting and running

    vm1.stop()
    volume.attach(vm1)
    vm1.start()

    test_util.test_dsc('create snapshot')
    snapshots = test_obj_dict.get_volume_snapshot(volume.get_volume().uuid)
    snapshots.create_snapshot('create_snapshot1', False)
#    snapshots.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create Snapshot test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
