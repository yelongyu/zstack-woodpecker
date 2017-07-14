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

USERGATEWAY = '192.168.0.211'
date_s = time.strftime('%m%d%S', time.localtime())
test_obj_dict = test_state.TestStateDict()
ks_inv = None
datacenter_inv = None
user_vpn_gw_inv = None

def test():
    global ks_inv
    global datacenter_inv
    global user_vpn_gw_inv
    datacenter_type = os.getenv('datacenterType')
    ks_existed = hyb_ops.query_aliyun_key_secret()
    if not ks_existed:
        ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    datacenter_list = hyb_ops.get_datacenter_from_remote(datacenter_type)
    regions = [ i.regionId for i in datacenter_list]
    for r in regions:
        if 'shanghai' in r:
            region_id = r
    datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, region_id, 'datacenter for test')
    iz_list = hyb_ops.get_identity_zone_from_remote(datacenter_type, region_id)
    zone_id = iz_list[-1].zoneId
    hyb_ops.add_identity_zone_from_remote(datacenter_type, datacenter_inv.uuid, zone_id)
    user_vpn_gw_inv = hyb_ops.create_vpc_user_vpn_gateway(datacenter_inv.uuid, gw_ip=USERGATEWAY, gw_name="ZStack-Vpc-User-Vpn-Gateway-Test")
    time.sleep(5)
    hyb_ops.del_vpc_user_vpn_gateway_remote(user_vpn_gw_inv.uuid)
    test_util.test_pass('Create Delete Vpc User Vpn Gateway Remote Test Success')

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
