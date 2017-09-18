'''

New Integration Test for delete exported image from image store.

@author: Mirabel
'''
import time
import os
import re

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

    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    for bs in backup_storage_list:
        if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
            break
    else:
        vm.destroy()
        test_util.test_skip('Not find image store type backup storage.')

    #vm1.check()
    vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
    root_volume_uuid = vm_root_volume_inv.uuid

    image_creation_option.set_root_volume_uuid(root_volume_uuid)
    image_creation_option.set_name('test_create_vm_images_vm')
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

    bs_dir = os.environ.get('sftpBackupStorageUrl')

    exported_image1_id = re.match(r'image-(.*)\.qcow2',image1_url.split('/')[-1]).group(1)
    exported_image1_path = "%s/export/image-%s.qcow2" % (bs_dir, exported_image1_id)
    related_file_1 = "%s/export/%s.qcow2" % (bs_dir, exported_image1_id)
    related_file_2 = "%s/export/%s.imf" % (bs_dir, exported_image1_id)
    related_file_3 = "%s/export/download-%s" % (bs_dir, exported_image1_id)

    if not test_lib.lib_check_backup_storage_file_exist(bs, exported_image1_path):
       test_util.test_fail('image (%s) is expected to be exported' % exported_image1_path)

    image1.delete_exported_image()

    if test_lib.lib_check_backup_storage_file_exist(backup_storage_list[0], exported_image1_path):                                                                                                                                                                
       test_util.test_fail('exported image (%s) is expected to be deleted' % exported_image1_path)
    if test_lib.lib_check_backup_storage_file_exist(backup_storage_list[0], related_file_1):                                                                                                                                                                  
       test_util.test_fail('%s is expected to be deleted' % related_file_1)
    if test_lib.lib_check_backup_storage_file_exist(backup_storage_list[0], related_file_2):                                                                                                                                                                  
       test_util.test_fail('%s is expected to be deleted' % related_file_2)
    if test_lib.lib_check_backup_storage_file_exist(backup_storage_list[0], related_file_3):                                                                                                                                                                  
       test_util.test_fail('%s is expected to be deleted' % related_file_3)


    exported_image2_id = re.match(r'image-(.*)\.qcow2',image2_url.split('/')[-1]).group(1)
    exported_image2_path = "%s/export/image-%s.qcow2" % (bs_dir, exported_image2_id)
    related_file_1 = "%s/export/%s.qcow2" % (bs_dir, exported_image2_id)
    related_file_2 = "%s/export/%s.imf" % (bs_dir, exported_image2_id)
    related_file_3 = "%s/export/download-%s" % (bs_dir, exported_image2_id)
    
    if not test_lib.lib_check_backup_storage_file_exist(backup_storage_list[0], exported_image2_path):
       test_util.test_fail('image (%s) is expected to be exported' % exported_image2_path)

    image2.delete_exported_image()

    if test_lib.lib_check_backup_storage_file_exist(backup_storage_list[0], exported_image2_path):                                                                                                                                                                 
       test_util.test_fail('exported image (%s) is expected to be deleted' % exported_image2_path)
    if test_lib.lib_check_backup_storage_file_exist(backup_storage_list[0], related_file_1):                                                                                                                                                                  
       test_util.test_fail('%s is expected to be deleted' % related_file_1)
    if test_lib.lib_check_backup_storage_file_exist(backup_storage_list[0], related_file_2):                                                                                                                                                                  
       test_util.test_fail('%s is expected to be deleted' % related_file_2)
    if test_lib.lib_check_backup_storage_file_exist(backup_storage_list[0], related_file_3):                                                                                                                                                                  
       test_util.test_fail('%s is expected to be deleted' % related_file_3)

    #do vm check before snapshot check
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Expose Image Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
