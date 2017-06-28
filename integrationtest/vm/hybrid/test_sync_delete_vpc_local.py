'''

Test sync & delete vpc in local.

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
vpc_inv = None


def test():
    global ks_inv
    global datacenter_inv
    global vpc_local
    global vpc_inv
    datacenter_type = os.getenv('datacenterType')
    ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    datacenter_list = hyb_ops.get_datacenter_from_remote(datacenter_type)
    region_id = datacenter_list[0].regionId
    datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, region_id, 'datacenter for test')
    hyb_ops.create_ecs_vpc_remote(datacenter_inv.uuid, 'vpc_for_test_%s' % date_s, '192.168.0.0/16')
    time.sleep(5)
    vpc_auto_synced = hyb_ops.query_ecs_vpc_local()
    if vpc_auto_synced:
        for v in vpc_auto_synced:
            hyb_ops.del_ecs_vpc_local(v.uuid)
    vpc_sync = hyb_ops.sync_ecs_vpc_from_remote(datacenter_inv.uuid)
    assert vpc_sync.addList
    vpc_local = hyb_ops.query_ecs_vpc_local()
    for vl in vpc_local:
        if vl.vpcName == 'vpc_for_test_%s' % date_s:
            vpc_inv = vl
    assert vpc_inv.uuid
    test_util.test_pass('Sync Delete Ecs Vpc Test Success')

def env_recover():
    global vpc_inv
    if vpc_inv:
        time.sleep(10)
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
