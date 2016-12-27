'''
test for sync image in newly add vcenter
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstacklib.utils.ssh as ssh
import test_stub
import os



img_uuid = None

vcenter_uuid1 = None
vcenter_uuid2 = None

mevoco1_ip = None
mevoco2_ip = None

delete_policy1 = None
delete_policy2 = None


def test():
    global vcenter_uuid1
    global vcenter_uuid2
    global mevoco1_ip
    global mevoco2_ip
    global img_uuid
    global delete_policy1
    global delete_policy2

    print os.environ
    vcenter1_name = os.environ['vcenter2_name']
    vcenter1_domain_name = os.environ['vcenter2_ip']
    vcenter1_username = os.environ['vcenter2_domain_name']
    vcenter1_password = os.environ['vcenter2_password']
    sync_image_url = os.environ['vcenter2_sync_image_url']
    image_name = os.environ['vcenter2_sync_image_name']

    mevoco1_ip = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']
    mevoco2_ip = os.environ['serverIp2']


    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    delete_policy1 = test_lib.lib_set_delete_policy('image', 'Delay')
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid1 = inv.uuid
    if vcenter_uuid1 == None:
        test_util.test_fail("vcenter_uuid is None")


    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    delete_policy2 = test_lib.lib_set_delete_policy('image', 'Delay')
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid2 = inv.uuid
    if vcenter_uuid2 == None:
        test_util.test_fail("vcenter_uuid is None")

    #bs_cond = res_ops.gen_query_conditions("name", '=', "vCenter[vm-center]")
    bs_cond = res_ops.gen_query_conditions("type", '=', "VCenter")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, \
            None, fields=['uuid'])
    if not bss:
        test_util.test_skip("not find available backup storage. Skip test")

    #add sync image in mevoco2
    image_option = test_util.ImageOption()
    image_option.set_name(image_name)
    #image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_format('vmtx')
    image_option.set_system_tags('vcenter::datacenter::datacenter1')
    #image_option.set_url(os.environ.get(sync_image_url))
    image_option.set_url(sync_image_url)
    image_option.set_backup_storage_uuid_list([bss[0].uuid])


    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)

    #if a error happens here, check whether the image with the same name is already
    #exist in vcenter, which is also raise exception about can't download on all backup storage
    test_util.test_logger("add image from url:%s" %(sync_image_url))
    new_image.add_root_volume_template()


    #reconnect vcenter and check newly add image in mevoco1
    test_util.test_logger("check image sync from mevoco1")
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    bs_cond = res_ops.gen_query_conditions("type", '=', "VCenter")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, None, fields=['uuid'])
    bs_ops.reconnect_backup_storage(bss[0].uuid)
    image_cond = res_ops.gen_query_conditions("name", '=', image_name)
    img_inv = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, None, fields=['uuid'])[0]
    img_uuid = img_inv.uuid
    if not img_uuid:
        test_util.test_fail("local woodpecker image uuid is null")


    #delete image in mevoco2
    test_util.test_logger("delete image from mevoco2")
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    image_cond = res_ops.gen_query_conditions("name", '=', image_name)
    img_inv = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, None, fields=['uuid'])[0]
    img_uuid = img_inv.uuid
    img_ops.delete_image(img_uuid)
    img_ops.expunge_image(img_uuid)

    #check image in mevoco1
    test_util.test_logger("check image delete sync from mevoco1")
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    bs_cond = res_ops.gen_query_conditions("type", '=', "VCenter")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, None, fields=['uuid'])
    bs_ops.reconnect_backup_storage(bss[0].uuid)
    image_cond = res_ops.gen_query_conditions("name", '=', image_name)
    img_inv = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, None, fields=['uuid'])[0]
    img_uuid = img_inv.uuid
    if img_uuid:
        test_util.test_fail("local woodpecker image is not deleted as expected")


    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_lib.lib_set_delete_policy('image', delete_policy2)
    if vcenter_uuid2:
        vct_ops.delete_vcenter(vcenter_uuid2)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_lib.lib_set_delete_policy('image', delete_policy1)
    if vcenter_uuid1:
        vct_ops.delete_vcenter(vcenter_uuid1)

    test_util.test_pass("vcenter sync image test passed.")



def error_cleanup():
    global vcenter_uuid1
    global vcenter_uuid2
    global mevoco2_ip
    global img_uuid
    global delete_policy1
    global delete_policy2

    test_lib.lib_set_delete_policy('image', delete_policy1)
    if img_uuid:
        img_ops.delete_image(img_uuid)
        img_ops.expunge_image(img_uuid)

    if vcenter_uuid1:
        vct_ops.delete_vcenter(vcenter_uuid1)

    if vcenter_uuid2:
        os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
        test_lib.lib_set_delete_policy('image', delete_policy2)
        vct_ops.delete_vcenter(vcenter_uuid2)

