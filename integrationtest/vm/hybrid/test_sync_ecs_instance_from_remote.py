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

date_s = time.strftime('%m%d-%H%M%S', time.localtime())
test_obj_dict = test_state.TestStateDict()
ks_inv = None
datacenter_inv = None
bucket_inv = None
vpc_inv = None
vswitch_inv = None
iz_inv = None
sg_inv = None
ecs_inv = None

def test():
    global ks_inv
    global datacenter_inv
    global bucket_inv
    global sg_inv
    global iz_inv
    global vswitch_inv
    global vpc_inv
    global ecs_inv
    datacenter_type = os.getenv('datacenterType')
    ecs_image_id = os.getenv('ecs_imageId')
#     cond_image = res_ops.gen_query_conditions('name', '=', os.getenv('imageName_i_c7'))
#     image =  res_ops.query_resource(res_ops.IMAGE, cond_image)[0]
#     bs_uuid = image.backupStorageRefs[0].backupStorageUuid
    cond_offering = res_ops.gen_query_conditions('name', '=', os.getenv('instanceOfferingName_m'))
    instance_offering = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond_offering)[0]
    ks_existed = hyb_ops.query_aliyun_key_secret()
    if not ks_existed:
        ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    datacenter_list = hyb_ops.get_datacenter_from_remote(datacenter_type)
    regions = [ i.regionId for i in datacenter_list]
    for r in regions:
        if 'shanghai' in r:
            region_id = r
#     region_id = datacenter_list[0].regionId
    datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, region_id, 'datacenter for test')
    bucket_inv = hyb_ops.create_oss_bucket_remote(datacenter_inv.uuid, 'zstack-test-%s-%s' % (date_s, region_id), 'created-by-zstack-for-test')
    hyb_ops.attach_oss_bucket_to_ecs_datacenter(bucket_inv.uuid)
    iz_list = hyb_ops.get_identity_zone_from_remote(datacenter_type, region_id)
    zone_id = iz_list[0].zoneId
#     hyb_ops.update_image_guestOsType(image.uuid, guest_os_type='CentOS')
    iz_inv = hyb_ops.add_identity_zone_from_remote(datacenter_type, datacenter_inv.uuid, zone_id)
    vpc_inv = hyb_ops.create_ecs_vpc_remote(datacenter_inv.uuid, 'vpc_for_test', '172.16.0.0/12')
    time.sleep(10)
    vswitch_inv = hyb_ops.create_ecs_vswtich_remote(vpc_inv.uuid, iz_inv.uuid, 'zstack-test-vswitch', '172.18.1.0/24')
    sg_inv = hyb_ops.create_ecs_security_group_remote('sg_for_test', vpc_inv.uuid)
    time.sleep(10)
    hyb_ops.sync_ecs_image_from_remote(datacenter_inv.uuid)
    ecs_image = hyb_ops.query_ecs_image_local()
    for i in ecs_image:
        if i.ecsImageId == ecs_image_id:
            image = i
    ecs_inv = hyb_ops.create_ecs_instance_from_ecs_image('Password123', image.uuid, vswitch_inv.uuid, instance_offering.uuid,
                                                         ecs_bandwidth=5, ecs_security_group_uuid=sg_inv.uuid, name='zstack-ecs-test')
    ecs_instance_auto_synced = hyb_ops.query_ecs_instance_local()
    for e in ecs_instance_auto_synced:
        if e.name == 'zstack-ecs-test':
            hyb_ops.del_ecs_instance_local(e.uuid)
    hyb_ops.sync_ecs_instance_from_remote(datacenter_inv.uuid)
    ecs_instance_local = hyb_ops.query_ecs_instance_local()
    for el in ecs_instance_local:
        if el.name == 'zstack-ecs-test':
            ecs_inv = el
    assert ecs_inv.uuid
    test_util.test_pass('Sync Ecs Instance From Remote Test Success')

def env_recover():
    global ecs_inv
    global datacenter_inv
    if ecs_inv:
        hyb_ops.stop_ecs_instance(ecs_inv.uuid)
        for _ in xrange(600):
            hyb_ops.sync_ecs_instance_from_remote(datacenter_inv.uuid)
            ecs_inv = [e for e in hyb_ops.query_ecs_instance_local() if e.name == 'zstack-ecs-test'][0]
            if ecs_inv.ecsStatus.lower() == "stopped":
                break
            else:
                time.sleep(1)
        hyb_ops.del_ecs_instance(ecs_inv.uuid)
    global sg_inv
    if sg_inv:
        time.sleep(30)
        hyb_ops.del_ecs_security_group_remote(sg_inv.uuid)
    global vswitch_inv
    if vswitch_inv:
        time.sleep(10)
        hyb_ops.del_ecs_vswitch_remote(vswitch_inv.uuid)
    global vpc_inv
    if vpc_inv:
        time.sleep(10)
        hyb_ops.del_ecs_vpc_remote(vpc_inv.uuid)
    global iz_inv
    if iz_inv:
        hyb_ops.del_identity_zone_in_local(iz_inv.uuid)

    global bucket_inv
    if bucket_inv:
        bucket_file = hyb_ops.get_oss_bucket_file_from_remote(bucket_inv.uuid).files
        if bucket_file:
            for i in bucket_file:
                hyb_ops.del_oss_bucket_file_remote(bucket_inv.uuid, i)
        time.sleep(10)
        hyb_ops.del_oss_bucket_remote(bucket_inv.uuid)
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
