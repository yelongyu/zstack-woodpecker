'''

New Integration Test for importing image when add imagestore backupstorage.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    bs_list = res_ops.query_resource(res_ops.IMAGE_STORE_BACKUP_STORAGE)
    images = res_ops.query_resource(res_ops.IMAGE)
    image_name_list = [img.name for img in images]
    for _bs in bs_list:
        bs_ops.delete_backup_storage(_bs.uuid)

    time.sleep(10)

    for bs in bs_list:
        bs_option = test_util.ImageStoreBackupStorageOption()
        bs_option.set_name(bs.name)
        bs_option.set_url(bs.url)
        bs_option.set_hostname(bs.hostname)
        bs_option.set_password('password')
        bs_option.set_sshPort(bs.sshPort)
        bs_option.set_username(bs.username)
        bs_option.set_import_images('true')
        bs_inv = bs_ops.create_image_store_backup_storage(bs_option)

        for zone_uuid in bs.attachedZoneUuids:
            bs_ops.attach_backup_storage(bs_inv.uuid, zone_uuid)

    time.sleep(10)

    _bs_list = res_ops.query_resource(res_ops.IMAGE_STORE_BACKUP_STORAGE)
    _images = res_ops.query_resource(res_ops.IMAGE)
    _image_name_list = [_img.name for _img in _images]

    if set([bs.name for bs in bs_list]) != set([_bs.name for _bs in _bs_list]):
        test_util.test_fail("Add ImageStore backupstorage failed")

    if set(image_name_list) != set(_image_name_list):
        test_util.test_fail("Import image failed when add ImageStore backupstorage")

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Add ImageStore backupstorage with image importing test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
