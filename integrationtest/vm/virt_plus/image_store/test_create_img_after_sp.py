'''

New Integration Test for creating image after doing volume snapshot

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

def test():
    vm = test_stub.create_vm(vm_name = 'basic-test-vm', image_name = 'image_for_sg_test')
    test_obj_dict.add_vm(vm)
    vm1 = test_stub.create_vm(vm_name = 'basic-test-vm1', image_name = 'image_for_sg_test')
    test_obj_dict.add_vm(vm1)

    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm1.vm)
    for bs in backup_storage_list:
        if bs.type in [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE, inventory.CEPH_BACKUP_STORAGE_TYPE]:
            image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
            break
    else:
        vm.destroy()
        vm1.destroy()
        test_util.test_skip('Not find image store or ceph type backup storage.')

    #vm1.check()
    vm_root_volume_inv = test_lib.lib_get_root_volume(vm1.get_vm())
    root_image_uuid = vm_root_volume_inv.rootImageUuid
    vm_img_inv = test_lib.lib_get_image_by_uuid(root_image_uuid)
    test_util.test_dsc('create snapshot and check')
    snapshots = test_obj_dict.get_volume_snapshot(vm_root_volume_inv.uuid)
    snapshots.set_utility_vm(vm)
    snapshots.create_snapshot('create_root_snapshot1')
    snapshot1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_root_snapshot2')

    image_creation_option.set_root_volume_uuid(vm_root_volume_inv.uuid)
    image_creation_option.set_name('test_create_vm_images_vm1')
    image_creation_option.set_timeout(600000)
    #image_creation_option.set_platform('Linux')
#     bs_type = backup_storage_list[0].type
#     if bs_type == 'Ceph':
#         origin_interval = conf_ops.change_global_config('ceph', 'imageCache.cleanup.interval', '1')

    image1 = test_image.ZstackTestImage()
    image1.set_creation_option(image_creation_option)
    image1.create()
    test_obj_dict.add_image(image1)
    image1.check()
    vm2 = test_stub.create_vm(image_name = 'test_create_vm_images_vm1')
    test_obj_dict.add_vm(vm2)

    #do vm check before snapshot check
    vm.check()
    vm1.stop()
    snapshots.check()
    snapshots.use_snapshot(snapshot1)
    vm1.start()
    snapshots.create_snapshot('create_root_snapshot1.1')
    
    image_creation_option.set_name('test_create_vm_images_vm2')
    image2 = test_image.ZstackTestImage()
    image2.set_creation_option(image_creation_option)
    image2.create()
    test_obj_dict.add_image(image2)
    image2.check()
    vm3 = test_stub.create_vm(image_name = 'test_create_vm_images_vm2')
    test_obj_dict.add_vm(vm3)
    snapshots.check()
    vm2.check()
    vm3.check()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create VM Image in Image Store Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
