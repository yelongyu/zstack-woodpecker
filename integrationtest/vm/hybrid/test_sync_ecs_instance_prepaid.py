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

def test():
    global ks_inv
    global datacenter_inv
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
        datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, r, 'datacenter for test')
        hyb_ops.sync_ecs_vpc_from_remote(datacenter_inv.uuid)
        vpc_local = hyb_ops.query_ecs_vpc_local()
        for vpc in vpc_local:
            hyb_ops.sync_ecs_security_group_from_remote(vpc.uuid)
        # Add Identity Zone
        iz_list = hyb_ops.get_identity_zone_from_remote(datacenter_type, r)
        ecs_prepaid_list = []
        for iz in iz_list:
            if not iz.availableInstanceTypes:
                continue
            iz_inv = hyb_ops.add_identity_zone_from_remote(datacenter_type, datacenter_inv.uuid, iz.zoneId)
            ecs_prepaid_list = [ep for ep in hyb_ops.sync_ecs_instance_from_remote(datacenter_inv.uuid, only_zstack='false') if ep.chargeType == 'PrePaid']
            if ecs_prepaid_list:
                break
            else:
                hyb_ops.del_identity_zone_in_local(iz_inv.uuid)
        if ecs_prepaid_list:
            break
        else:
            hyb_ops.del_datacenter_in_local(datacenter_inv.uuid)
    if not ecs_prepaid_list:
        test_util.test_fail("Prepaid ECS was not found in all available dataCenter")
    ecs_instance_local = hyb_ops.query_ecs_instance_local()
    for el in ecs_instance_local:
        if el.chargeType == 'PrePaid':
            ecs_inv = el
    assert ecs_inv.expireDate
    test_util.test_pass('Sync Prepaid ECS Instance Test Success')

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
