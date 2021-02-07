'''

New Integration Test for resizing data volume.

@author: czhou25
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

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
    vol_size = volume.volume.size
    image_name = os.environ.get('imageName_net')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm = test_stub.create_vm("test_resize_vm", image_name, l3_name)
    vm.check()
    test_obj_dict.add_vm(vm)
    volume.attach(vm)
    vm.stop()
    vm.check()

    set_size = 1024*1024*1024*5
    vol_ops.resize_data_volume(volume_uuid, set_size)
    vm.update()
    vol_size_after = test_lib.lib_get_data_volumes(vm.get_vm())[0].size
    if set_size != vol_size_after:
        test_util.test_fail('Resize Data Volume failed, size = %s' % vol_size_after)

    bs_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    image_option = test_util.ImageOption()
    image_option.set_data_volume_uuid(volume_uuid)
    image_option.set_name('data_resize_template')
    image_option.set_backup_storage_uuid_list([bs_list[0].uuid])
    data_image = img_ops.create_data_volume_template(image_option)
    target_host = test_lib.lib_find_random_host(vm.get_vm())

    new_data = vol_ops.create_volume_from_template(data_image.uuid, volume.volume.primaryStorageUuid, host_uuid = target_host.uuid)
    if set_size != new_data.size:
        test_util.test_fail('Resize Data Volume failed, size = %s' % new_data.size)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Resize Data Volume Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
