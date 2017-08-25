'''

New Integration Test for hybrid.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import os

date_s = time.strftime('%m%d-%H%M%S', time.localtime())
test_obj_dict = test_state.TestStateDict()
ks_inv = None
datacenter_inv = None
bucket_inv = None

def test():
    global ks_inv
    global datacenter_inv
    global bucket_inv
    datacenter_type = os.getenv('datacenterType')
    cond_image = res_ops.gen_query_conditions('name', '=', os.getenv('imageName_s'))
    image =  res_ops.query_resource(res_ops.IMAGE, cond_image)[0]
    bs_uuid = image.backupStorageRefs[0].backupStorageUuid
    ks_existed = hyb_ops.query_aliyun_key_secret()
    if not ks_existed:
        ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    # Clear datacenter remained in local
    datacenter_local = hyb_ops.query_datacenter_local()
    if datacenter_local:
        for d in datacenter_local:
            hyb_ops.del_datacenter_in_local(d.uuid)
    datacenter_list = hyb_ops.get_datacenter_from_remote(datacenter_type)
    regions = [ i.regionId for i in datacenter_list]
    for r in regions:
        if 'shanghai' in r:
            region_id = r
    datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, region_id, 'datacenter for test')
    bucket_inv = hyb_ops.create_oss_bucket_remote(datacenter_inv.uuid, 'zstack-test-%s-%s' % (date_s, region_id), 'created-by-zstack-for-test')
    hyb_ops.attach_oss_bucket_to_ecs_datacenter(bucket_inv.uuid)
    hyb_ops.update_image_guestOsType(image.uuid, guest_os_type='CentOS')
    ecs_image_inv = hyb_ops.create_ecs_image_from_local_image(bs_uuid, datacenter_inv.uuid, image.uuid, name='zstack-test-ecs-image')
    time.sleep(10)
    hyb_ops.del_ecs_image_remote(ecs_image_inv.uuid)
    bucket_file = hyb_ops.get_oss_bucket_file_from_remote(bucket_inv.uuid).files
    if bucket_file:
        time.sleep(20)
        for i in bucket_file:
            hyb_ops.del_oss_bucket_file_remote(bucket_inv.uuid, i)
    time.sleep(10)
    hyb_ops.del_oss_bucket_remote(bucket_inv.uuid)
    test_util.test_pass('Create Delete Ecs Image Test Success')

def env_recover():
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
