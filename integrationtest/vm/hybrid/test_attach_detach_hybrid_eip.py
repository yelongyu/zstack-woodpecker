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
test_stub = test_lib.lib_get_test_stub()
ks_inv = None
datacenter_inv = None
bucket_inv = None
vpc_inv = None
vswitch_inv = None
iz_inv = None
sg_inv = None
ecs_inv = None
eip_inv = None

def test():
    global ks_inv
    global datacenter_inv
    global bucket_inv
    global sg_inv
    global iz_inv
    global vswitch_inv
    global vpc_inv
    global ecs_inv
    global eip_inv
    datacenter_type = os.getenv('datacenterType')
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
#     region_id = datacenter_list[0].regionId
    datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, region_id, 'datacenter for test')
    ecs_inv = test_stub.create_ecs_instance(datacenter_type, datacenter_inv.uuid, region_id)
    hyb_ops.sync_hybrid_eip_from_remote(datacenter_inv.uuid)
    eip_all = hyb_ops.query_hybrid_eip_local()
    eip_available = [eip for eip in eip_all if eip.status.lower() == 'available']
    if eip_available:
        eip_inv = eip_available[0]
    else:
        eip_inv = hyb_ops.create_hybrid_eip(datacenter_inv.uuid, 'zstack-test-eip', '1')
    hyb_ops.attach_hybrid_eip_to_ecs(eip_inv.uuid, ecs_inv.uuid)
    time.sleep(5)
    hyb_ops.detach_hybrid_eip_from_ecs(eip_inv.uuid)
    test_util.test_pass('Attach Detach Hybrid Eip to/from Ecs Test Success')

def env_recover():
    global ecs_inv
    global datacenter_inv
    if ecs_inv:
        test_stub.delete_ecs_instance(datacenter_inv, ecs_inv)

    global iz_inv
    if iz_inv:
        hyb_ops.del_identity_zone_in_local(iz_inv.uuid)

    if datacenter_inv:
        hyb_ops.del_datacenter_in_local(datacenter_inv.uuid)

    global ks_inv
    if ks_inv:
        hyb_ops.del_aliyun_key_secret(ks_inv.uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
