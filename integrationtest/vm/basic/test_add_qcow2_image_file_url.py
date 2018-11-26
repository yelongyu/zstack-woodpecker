'''
test for adding file:///image.qcow2
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
        if bs.type == 'AliyunEBS':
            continue
    else:
        test_util.test_skip('Not find image store type backup storage.')

    image_option = test_util.ImageOption()
    image_option.set_format('qcow2')
    image_option.set_name('test_file_url_image')
    image_option.set_system_tags('qemuga')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url("file:///etc/issue")
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(60000)

    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)

    new_image.add_root_volume_template()
    new_image.delete()

    test_util.test_pass('test add file:///image.qcow2 passed.')



#Will be called only if exception happens in test().
def error_cleanup():
    global new_image
    if new_image:
        new_image.delete()
    pass
