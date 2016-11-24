'''
New Integration Test for adding image with system tag qemuga.
@author: SyZhao
'''


import os

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.test_lib as test_lib


_config_ = {
        'timeout' : 9500,
        'noparallel' : False
        }

new_image = None


def test():
    global new_image

    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, \
            None)
    if not bss:
        test_util.test_skip("not find available backup storage. Skip test")

    for bs in bss:
        if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            break
        if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
            break
        if bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
            break
    else:
        test_util.test_skip('Not find image store type backup storage.')

    image_option = test_util.ImageOption()
    image_option.set_format('iso')
    image_option.set_name('test_negative_raw')
    image_option.set_system_tags('qemuga')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url(os.environ.get('negativeImageUrl'))
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(3600*1000)

    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)

    ret = new_image.add_root_volume_template()

    if not ret:
        test_util.test_fail('test add negative image failed.')
    else:
        test_util.test_pass('test add negative image passed.')

    new_image.delete()
    #new_image.expunge([bss[0].uuid])

#Will be called only if exception happens in test().
def error_cleanup():
    global new_image
    if new_image:
        new_image.delete()
    pass
