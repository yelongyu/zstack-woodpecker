'''

New Integration Test for creating image for image store feature.

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
import zstackwoodpecker.operations.config_operations as conf_ops

_config_ = {
        'timeout' : 2200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_specific_stub()
test_obj_dict = test_state.TestStateDict()
default_snapshot_depth = None
test_depth = 120

def test():
    vm1 = test_stub.create_vm(vm_name = 'basic-test-vm')
    test_obj_dict.add_vm(vm1)
    vm1.check()
    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm1.vm)
    for bs in backup_storage_list:
        if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
            break
    else:
        vm1.destroy()
        test_util.test_skip('Not find image store type backup storage.')

    global default_snapshot_depth
    default_snapshot_depth = conf_ops.change_global_config('volumeSnapshot', \
            'incrementalSnapshot.maxNum', test_depth)
    image_creation_option.set_root_volume_uuid(vm1.vm.rootVolumeUuid)
    test_img_num = 1
    while (test_img_num < 101):
        image_creation_option.set_name('test_create_img_store_img_vm%d' % test_img_num)
    #image_creation_option.set_platform('Linux')
        image = test_image.ZstackTestImage()
        image.set_creation_option(image_creation_option)
        image.create()
        # image.check()
        test_obj_dict.add_image(image)
        test_img_num += 1

    vm2 = test_stub.create_vm(image_name = 'test_create_img_store_img_vm100')
    test_obj_dict.add_vm(vm2)
    vm2.check()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create 100 images Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global default_snapshot_depth
    conf_ops.change_global_config('volumeSnapshot', \
            'incrementalSnapshot.maxNum', default_snapshot_depth)

    test_lib.lib_error_cleanup(test_obj_dict)

