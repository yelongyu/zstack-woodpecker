'''

Create 2 VMs with same image. Then commit 2 new images from 2 VMs.

@author: Youyk
'''
import time
import os

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm

test_stub = test_lib.lib_get_specific_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    vm1 = test_stub.create_vm(vm_name = 'basic-test-vm')
    test_obj_dict.add_vm(vm1)
    #vm1.check()
    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm1.vm)
    for bs in backup_storage_list:
        if bs.type in [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE, inventory.CEPH_BACKUP_STORAGE_TYPE]:
            image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
            break
    else:
        vm1.destroy()
        test_util.test_skip('Not find image store or ceph type backup storage.')

    vm2 = test_stub.create_vm(vm_name = 'basic-test-vm')
    test_obj_dict.add_vm(vm2)

    image_creation_option.set_root_volume_uuid(vm1.vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_vm_images_with_same_name')
    #image_creation_option.set_platform('Linux')

    image1 = test_image.ZstackTestImage()
    image1.set_creation_option(image_creation_option)
    image1.create()
    test_obj_dict.add_image(image1)
    image1.check()

    vm1.destroy()

    image_creation_option.set_root_volume_uuid(vm2.vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_vm_images_with_same_name')
    image2 = test_image.ZstackTestImage()
    image2.set_creation_option(image_creation_option)
    image2.create()
    test_obj_dict.add_image(image2)
    image2.check()

    vm3 = test_stub.create_vm(image_name = 'test_create_vm_images_with_same_name')
    test_obj_dict.add_vm(vm3)
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create 2 VM images from same origin Image Successfully')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
