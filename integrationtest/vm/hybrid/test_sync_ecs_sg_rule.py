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
vpc_inv = None
sg_inv = None

def test():
    global ks_inv
    global datacenter_inv
    global vpc_inv
    global sg_inv
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
    hyb_ops.sync_ecs_vpc_from_remote(datacenter_inv.uuid)
    vpc_all = hyb_ops.query_ecs_vpc_local()
    ecs_vpc = [vpc for vpc in vpc_all if vpc.status.lower() == 'available']
    if ecs_vpc:
        vpc_inv = ecs_vpc[0]
    else:
        vpc_inv = hyb_ops.create_ecs_vpc_remote(datacenter_inv.uuid, 'vpc_for_test', 'zstack-test-vpc-vrouter', '172.16.0.0/12')
    time.sleep(5)
    sg_inv = hyb_ops.create_ecs_security_group_remote('sg_for_test_%s' % date_s, vpc_inv.uuid)
    time.sleep(5)
    hyb_ops.create_ecs_security_group_rule_remote(sg_inv.uuid, 'ingress', 'ALL', '-1/-1', '0.0.0.0/0', 'accept', 'intranet', '10')
    hyb_ops.create_ecs_security_group_rule_remote(sg_inv.uuid, 'egress', 'ALL', '-1/-1', '0.0.0.0/0', 'accept', 'intranet', '10')
    hyb_ops.sync_ecs_security_group_rule_from_remote(sg_inv.uuid)
    cond_sg_rule = res_ops.gen_query_conditions('ecsSecurityGroupUuid', '=', sg_inv.uuid)
    sg_rule = hyb_ops.query_ecs_security_group_rule_local(cond_sg_rule)
    assert sg_rule[0].priority == '10'
    test_util.test_pass('Sync Delete Ecs Security Group Test Success')

def env_recover():
    global sg_inv
    if sg_inv:
        hyb_ops.del_ecs_security_group_remote(sg_inv.uuid)

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
