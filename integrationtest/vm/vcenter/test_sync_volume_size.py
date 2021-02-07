'''
test sync volume size
@author: guocan
'''
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import test_stub

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict

    ova_image_name = os.environ['vcenterDefaultmplate']
    network_pattern1 = 'L3-%s'%os.environ['dportgroup']
    if not vct_ops.lib_get_vcenter_l3_by_name(network_pattern1):
        network_pattern1 = 'L3-%s'%os.environ['portgroup0']

    disk_offering1 = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))

    vm = test_stub.create_vm_in_vcenter(vm_name = 'test_for_sync_volume_size_vm', image_name = ova_image_name, l3_name = network_pattern1)
    test_obj_dict.add_vm(vm)
    vm.check()
    ps_uuid = vm.vm.allVolumes[0].primaryStorageUuid
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering1.uuid)
    volume_creation_option.set_name('test_for_sync_volume_size_volume')
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    #SyncVolumeSize
    vol_ops.sync_volume_size(volume.get_volume().uuid)
    volume.attach(vm)
    volume.check()
    vol_ops.sync_volume_size(volume.get_volume().uuid)

    #cleanup
    test_lib.lib_error_cleanup(test_obj_dict)

    test_util.test_pass("Test sync volume size in vcenter passed.")


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

  