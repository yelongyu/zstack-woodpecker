'''

ImageStore service will temporarily unavailable during gc(ReclaimSpaceFromImageStore).
This test is to validate the service locking during the space reclaiming of ImageStore Backup storage.
The expected error message is "image store service is temporary not available, because it is reclaiming space now"

@author: Legion
'''

import os
import sys
import traceback
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import apibinding.inventory as inventory
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import time

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
longjob = test_stub.Longjob(url=os.getenv('imageUrl_raw'))
volume_bandwidth = 10*1024*1024
volume_bandwidth2 = 1000*1024*1024
zstack_management_ip = os.getenv('zstackManagementIp')


def add_image(image_name, bs_uuid, url=None, img_format='qcow2'):
        url = url if url else os.path.join(os.getenv('imageServer'), 'iso/iso_for_install_vm_test.iso')
        img_option = test_util.ImageOption()
        img_option.set_name(image_name)
        img_option.set_format(img_format)
        img_option.set_backup_storage_uuid_list([bs_uuid])
        img_option.set_url(url)
        img_option.set_timeout(900000)
        if img_format == 'iso':
            image_inv = img_ops.add_iso_template(img_option)
        else:
            image_inv = img_ops.add_image(img_option)
        image = test_image.ZstackTestImage()
        image.set_image(image_inv)
        image.set_creation_option(img_option)
        return image

def test():
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for i in bs:
        if i.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            break
    else:
        test_util.test_logger('The BS type is: %s.' % i.type)
        test_util.test_skip('Skip test on non-imagestore bs')
    longjob.add_image()
    time.sleep(10)

    longjob.delete_image()
    longjob.expunge_image()

    cleanup_pid = os.fork()
    if cleanup_pid == 0:
        bs_ops.reclaim_space_from_bs(longjob.target_bs.uuid)
    else:
        try:
            add_image('iso_image', longjob.target_bs.uuid, img_format='iso')
            test_util.test_fail('Adding image is expected to be failed during space reclaiming, but it was success')
        except:
            test_util.test_pass('ImageStore BackupStorage Lock on GC Test Success')


#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
