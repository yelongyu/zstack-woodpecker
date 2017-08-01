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
vpc_inv = None
vr_name = 'zstack-test-vrouter-%s' % date_s

def test():
    global ks_inv
    global datacenter_inv
    global vpc_local
    global vpc_inv
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
    vpc_inv = hyb_ops.create_ecs_vpc_remote(datacenter_inv.uuid, 'vpc_for_test_%s' % date_s, vr_name, '192.168.0.0/16')
    time.sleep(5)
    hyb_ops.sync_aliyun_virtual_router_from_remote(vpc_inv.uuid)
    vr_local = hyb_ops.query_aliyun_virtual_router_local()
    for vr in vr_local:
        if vr.name == vr_name:
            _vr = vr
    assert _vr.vrId
    test_util.test_pass('Sync Aliyun Virtual Router Test Success')

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
