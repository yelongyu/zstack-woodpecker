'''
New Integration test for cold migration of data volume with snapshot between hosts.
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.header.host as host_header
import os

volume = None
vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    volume_creation_option = test_util.VolumeOption()
    test_util.test_dsc('Create volume and check')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume_uuid = volume.volume.uuid
    
    test_util.test_dsc('Create vm and check')
    vm = test_stub.create_vr_vm('migrate_volume_vm', 'imageName_net', 'l3VlanNetwork2')
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_uuid = vm.vm.uuid
    
    ps = test_lib.lib_get_primary_storage_by_uuid(vm.get_vm().allVolumes[0].primaryStorageUuid)
    if ps.type != inventory.LOCAL_STORAGE_TYPE:
        test_util.test_skip('Skip test on non-localstorage')
    
    volume.attach(vm)
    volume.detach(vm_uuid)

    snapshots = test_obj_dict.get_volume_snapshot(volume_uuid)
    snapshots.set_utility_vm(vm)
    snapshots.create_snapshot('create_snapshot1')
    snapshots.check()
    snapshots.create_snapshot('create_snapshot2')
    snapshots.check()

    target_host = test_lib.lib_find_random_host_by_volume_uuid(volume_uuid)
    target_host_uuid = target_host.uuid

    vol_ops.migrate_volume(volume_uuid, target_host_uuid)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Cold migrate Data Volume Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
