'''
test for adding image auto format.
@author: ronghao.Zhou
'''

import os

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.test_state as test_state

_config_ = {
    'timeout': 9500,
    'noparallel': False
}

test_dict=test_state.TestStateDict()

def test():
    global test_dict

    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, bs_cond)
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

    #test add iso
    image_option = test_util.ImageOption()
    image_option.set_format('qcow2')
    image_option.set_name('test_add_iso_image')
    # image_option.set_mediaType('ISO')
    image_option.set_url(os.environ.get('imageServer')+"/iso/CentOS-x86_64-7.2-Minimal.iso")
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(120000)
    image=img_ops.add_image(image_option)

    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)
    new_image.set_image(image)
    test_dict.add_image(new_image)

    image_cond = res_ops.gen_query_conditions('uuid', '=', new_image.get_image().uuid)
    image_inv = res_ops.query_resource(res_ops.IMAGE, image_cond)[0]
    if image_inv.format != 'iso':
        test_util.test_fail('image\'s format is not iso,fail')

    #test add qcow2

    image_option = test_util.ImageOption()
    image_option.set_format('iso')
    image_option.set_name('test_add_qcow2_image')
    # image_option.set_mediaType('ISO')
    image_option.set_url(os.environ.get('imageServer')+"/diskimages/core-image-minimal-qemux86-64_v1.qcow2")
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(120000)
    image=img_ops.add_image(image_option)

    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)
    new_image.set_image(image)
    test_dict.add_image(new_image)

    image_cond = res_ops.gen_query_conditions('uuid', '=', new_image.get_image().uuid)
    image_inv = res_ops.query_resource(res_ops.IMAGE, image_cond)[0]
    if bss[0].type!=inventory.CEPH_BACKUP_STORAGE_TYPE:
        if image_inv.format != 'qcow2':
            test_util.test_fail('image\'s format is not qcow2,fail')
    else:
        if image_inv.format!='raw':
            test_util.test_fail('image\' format is not raw,fail')

    #test add raw
    image_option = test_util.ImageOption()
    image_option.set_format('iso')
    image_option.set_name('test_add_raw_image')
    # image_option.set_mediaType('ISO')
    image_option.set_url(os.environ.get('imageServer')+"/diskimages/zstack_image_test.raw")
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(120000)
    image=img_ops.add_image(image_option)

    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)
    new_image.set_image(image)
    test_dict.add_image(new_image)

    image_cond = res_ops.gen_query_conditions('uuid', '=', new_image.get_image().uuid)
    image_inv = res_ops.query_resource(res_ops.IMAGE, image_cond)[0]
    if image_inv.format != 'raw':
        test_util.test_fail('image\'s format is not raw,fail')

    #test add other format
    image_option = test_util.ImageOption()
    image_option.set_format('qcow2')
    image_option.set_name('test_add_vmdk_image')
    # image_option.set_mediaType('ISO')
    image_option.set_url(os.environ.get('imageServer')+"/diskimages/zstack-image-1.2-flat.vmdk")
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(120000)
    image=img_ops.add_image(image_option)

    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)
    new_image.set_image(image)
    test_dict.add_image(new_image)

    image_cond = res_ops.gen_query_conditions('uuid', '=', new_image.get_image().uuid)
    image_inv = res_ops.query_resource(res_ops.IMAGE, image_cond)[0]
    if image_inv.format!='raw':
        test_util.test_fail('image\' format is not raw,fail')

    test_lib.lib_robot_cleanup(test_dict)
    test_util.test_pass('test add image auto format success!')


# Will be called only if exception happens in test().
def error_cleanup():
    global test_dict
    test_lib.lib_robot_cleanup(test_dict)
