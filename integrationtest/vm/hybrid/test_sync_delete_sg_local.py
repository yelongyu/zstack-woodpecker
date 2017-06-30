'''

Test sync & delete security group in local.

@author: Quarkonics
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
vpc_inv = None
sg_inv = None

def test():
    global ks_inv
    global datacenter_inv
    global vpc_inv
    global sg_inv
    datacenter_type = os.getenv('datacenterType')
    ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    datacenter_list = hyb_ops.get_datacenter_from_remote(datacenter_type)
    regions = [ i.regionId for i in datacenter_list]
    for r in regions:
        if 'shanghai' in r:
            region_id = r
#     region_id = datacenter_list[0].regionId
    datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, region_id, 'datacenter for test')
    vpc_inv = hyb_ops.create_ecs_vpc_remote(datacenter_inv.uuid, 'vpc_for_test', '192.168.0.0/16')
    time.sleep(5)
    hyb_ops.create_ecs_security_group_remote('sg_for_test_%s' % date_s, vpc_inv.uuid)
    time.sleep(5)
    sg_auto_synced = hyb_ops.query_ecs_security_group_local()
    if sg_auto_synced:
        for sg in sg_auto_synced:
            hyb_ops.del_ecs_security_group_in_local(sg.uuid)
    sg_sync = hyb_ops.sync_security_group_from_remote(vpc_inv.uuid)
    assert sg_sync.addList
    sg_local = hyb_ops.query_ecs_security_group_local()
    for sl in sg_local:
        if sl.securityGroupName == 'sg_for_test_%s' % date_s:
            sg_inv = sl
    assert sg_inv.uuid
    test_util.test_pass('Sync Delete Ecs Security Group Test Success')

def env_recover():
    global sg_inv
    if sg_inv:
        time.sleep(10)
        hyb_ops.del_ecs_security_group_remote(sg_inv.uuid)
    global vpc_inv
    if vpc_inv:
        time.sleep(5)
        hyb_ops.del_ecs_vpc_remote(vpc_inv.uuid)
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
