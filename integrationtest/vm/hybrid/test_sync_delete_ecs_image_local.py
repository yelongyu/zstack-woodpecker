'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import os

date_s = time.strftime('%m%d%S', time.localtime())
test_obj_dict = test_state.TestStateDict()
ks_inv = None
datacenter_inv = None
bucket_inv = None

def test():
    global ks_inv
    global datacenter_inv
    global bucket_inv
    datacenter_type = os.getenv('datacenterType')
    cond = res_ops.gen_query_conditions('name', '=', os.getenv('imageName_s'))
    image =  res_ops.query_resource(res_ops.IMAGE, cond)[0]
    bs_uuid = image.backupStorageRefs[0].backupStorageUuid
    try:
        ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    except:
        pass
    datacenter_list = hyb_ops.get_datacenter_from_remote(datacenter_type)
    regions = [ i.regionId for i in datacenter_list]
    err_list = []
    for region_id in regions:
        try:
            datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, region_id, 'datacenter for test')
        except hyb_ops.ApiError, e:
            err_list.append(e)
            pass
        if datacenter_inv:
            break
    if len(err_list) == len(regions):
        raise hyb_ops.ApiError("Failed to add DataCenter: %s" % err_list)
    bucket_inv = hyb_ops.create_oss_bucket_remote(region_id, 'zstack-test-%s-%s' % (date_s, region_id), 'created-by-zstack-for-test')
    hyb_ops.attach_oss_bucket_to_ecs_datacenter(bucket_inv.uuid, datacenter_inv.uuid)
    hyb_ops.update_image_guestOsType(image.uuid, guest_os_type='CentOS')
    hyb_ops.create_ecs_image_from_local_image(bs_uuid, datacenter_inv.uuid, image.uuid)
    time.sleep(5)
    ecs_image_auto_synced = hyb_ops.query_ecs_image_local()
    if ecs_image_auto_synced:
        for i in ecs_image_auto_synced:
            hyb_ops.del_ecs_image_in_local(i.uuid)
    hyb_ops.sync_ecs_image_from_remote(datacenter_inv.uuid)
    ecs_image_local = hyb_ops.query_ecs_image_local()
    for i in ecs_image_local:
        if i.name == image.name:
            ecs_image_inv = i
    hyb_ops.del_ecs_image_remote(ecs_image_inv.uuid)
    test_util.test_pass('Sync Delete Local Ecs Image Test Success')

def env_recover():
    global bucket_inv
    if bucket_inv:
        bucket_file = hyb_ops.get_oss_bucket_file_from_remote(bucket_inv.uuid).files
        if bucket_file:
            for i in bucket_file:
                hyb_ops.del_oss_bucket_file_remote(bucket_inv.uuid, i)
        time.sleep(10)
        hyb_ops.del_oss_bucket_remote(bucket_inv.uuid)
        #hyb_ops.del_oss_file_bucket_name_in_local(bucket_inv.uuid)
    global datacenter_inv
    if datacenter_inv:
        hyb_ops.del_datacenter_in_local(datacenter_inv.uuid)
    global ks_inv
    if ks_inv:
        hyb_ops.del_aliyun_key_secret(ks_inv.uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
