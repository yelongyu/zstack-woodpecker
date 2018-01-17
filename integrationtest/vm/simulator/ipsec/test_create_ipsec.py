'''

Test VPC IPsec

@author: Glody 
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.ipsec_operations as ipsec_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict1 = test_state.TestStateDict()
test_obj_dict2 = test_state.TestStateDict()
ipsec = None
vip1_uuid = None
vpc_vr = None

def test():
    global ipsec
    global vip1_uuid
    global vpc_vr
    cond = res_ops.gen_query_conditions('name', '=', 'public network') 
    public_network = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    vip1 = test_stub.create_vip('vip_ipsec', public_network.uuid)
    vip1_uuid = vip1.get_vip().uuid
    test_util.test_dsc('Create vpc vr and attach networks')
    vpc_vr = test_stub.create_vpc_vrouter()

    cond = res_ops.gen_query_conditions('name', '=', 'l3VlanNetwork11')
    l3_vlan_network11 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    vpc_vr.add_nic(l3_vlan_network11.uuid)

    peer_address = '10.94.10.10'
    
    try:
        ipsec = ipsec_ops.create_ipsec_connection('ipsec', None, peer_address, '123456', vip1_uuid, None)
    except:
        test_util.test_fail('Failed to create vpc ipsec')

    test_stub.delete_vip(vip1_uuid)
    vpc_vr.destroy()
    ipsec_ops.delete_ipsec_connection(ipsec.uuid)
    test_util.test_pass('Create VPC Ipsec Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global ipsec
    global vip1_uuid
    global vpc_vr
    if ipsec != None:
        ipsec_ops.delete_ipsec_connection(ipsec.uuid)
    if vip != None:
        test_stub.delete_vip(vip1_uuid)
    if vpc_vr != None:
        vpc_vr.destroy()
