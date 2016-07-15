'''

New Integration Test for export image from image store, after doing some snapshot and commit image ops.

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

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
exported_image_name1 = 'add_exported_image3'
exported_image_name2 = 'add_exported_image4'

def test():
    vm = test_stub.create_vm(vm_name = 'basic-test-vm', image_name = 'image_for_sg_test')
    test_obj_dict.add_vm(vm)
    vm1 = test_stub.create_vm(vm_name = 'basic-test-vm1', image_name = 'image_for_sg_test')
    test_obj_dict.add_vm(vm1)

    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm1.vm)
    for bs in backup_storage_list:
        if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
            break
    else:
        test_util.test_skip('Not find image store type backup storage.')

    #vm1.check()
    vm_root_volume_inv = test_lib.lib_get_root_volume(vm1.get_vm())
    root_volume_uuid = vm_root_volume_inv.uuid
    test_util.test_dsc('create snapshot and check')
    snapshots = test_obj_dict.get_volume_snapshot(root_volume_uuid)
    snapshots.set_utility_vm(vm)
    times = 1
    #create 20 snapshots.
    while (times < 21):
        snapshots.create_snapshot('create_root_snapshot_%s' % times)
        times += 1

    image_creation_option.set_root_volume_uuid(root_volume_uuid)
    image_creation_option.set_name('test_create_vm_images_vm1')
    image_creation_option.set_format('qcow2')
    #image_creation_option.set_platform('Linux')
    bs_type = backup_storage_list[0].type

    image1 = test_image.ZstackTestImage()
    image1.set_creation_option(image_creation_option)
    image1.create()
    test_obj_dict.add_image(image1)
    image1_url = image1.export()

    image_creation_option.set_url(image1_url)
    image_creation_option.set_name(exported_image_name1)
    image2 = test_image.ZstackTestImage()
    image2.set_creation_option(image_creation_option)
    image2.add_root_volume_template()
    test_obj_dict.add_image(image2)
    image2_url = image2.export()

    vm2 = test_stub.create_vm(image_name = exported_image_name1)
    test_obj_dict.add_vm(vm2)
    image_creation_option.set_url(image2_url)
    image_creation_option.set_name(exported_image_name2)
    image2 = test_image.ZstackTestImage()
    image2.set_creation_option(image_creation_option)
    image2.add_root_volume_template()

    vm3 = test_stub.create_vm(image_name = exported_image_name2)
    test_obj_dict.add_vm(vm3)

    #do vm check before snapshot check
    vm2.check()
    vm3.check()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Expose Image Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
