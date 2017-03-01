'''
New Integration Test for delete BS and import images when add BS.

@author: quarkonics
'''

import os
import time
import commands
#import sys

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstacklib.utils.ssh as ssh

_config_ = {
        'timeout' : 18000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def compare_image(image1, image2):
    fields = [ 'uuid', 'name', 'state', 'status', 'url', 'actualSize', 'description', 'format', 'mediaType', 'platform', 'size', 'system', 'type' ]
    for field in fields:
        if hasattr(image1, field) and getattr(image1, field) != getattr(image2, field):
            return False
    return True

def test():
    test_util.test_dsc('create image check timeout test')
    if res_ops.query_resource(res_ops.CEPH_BACKUP_STORAGE):
        bs = res_ops.query_resource(res_ops.CEPH_BACKUP_STORAGE)[0]
    else:
        test_util.test_skip("No ceph backupstorage for test. Skip test")
    cond = res_ops.gen_query_conditions('backupStorageRef.backupStorage.uuid', '=', bs.uuid)
    images =  res_ops.query_resource(res_ops.IMAGE, cond)

    #create backup storage on previous vm
    backup_storage_option = test_util.CephBackupStorageOption()
    backup_storage_option.name = bs.name
    backup_storage_option.monUrls = os.environ.get('cephBackupStorageMonUrls').split(';')
    backup_storage_option.importImages = "true"
    backup_storage_option.poolName = bs.poolName

    bs_ops.delete_backup_storage(bs.uuid)
    backup_storage_inventory = bs_ops.create_backup_storage(backup_storage_option)
    time.sleep(5)
    cond = res_ops.gen_query_conditions('backupStorageRef.backupStorage.uuid', '=', backup_storage_inventory.uuid)
    images_imported =  res_ops.query_resource(res_ops.IMAGE, cond)
    if len(images_imported) != len(images):
        test_util.test_fail("imported images has different number(%s) than original images(%s)" % (len(images_imported), len(images)))
    for image in images:
        image_match = False
        for ii in images_imported:
	    if compare_image(image, ii):
                image_match = True
        if not image_match:
            test_util.test_fail("images(%s) not imported correctly" % (image.uuid))


    test_lib.lib_error_cleanup(test_obj_dict)
