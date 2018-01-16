'''

Test attach l3network to VPC IPsec

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

def test():
    global mevoco1_ip
    global mevoco2_ip
    global ipsec1
    global ipsec2
    cond = res_ops.gen_query_conditions('name', '=', 'public network') 
    public_network = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    vip1 = test_stub.create_vip('vip1', public_network.uuid)

    test_util.test_dsc('Create vpc vr and attach networks')
    vpc_vr = test_stub.create_vpc_vrouter()

    cond = res_ops.gen_query_conditions('name', '=', 'l3VlanNetwork11')
    l3_vlan_network11 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    vpc_vr.add_nic(l3_vlan_network11.uuid)

    peer_address = '10.94.10.10'
    try:
        ipsec = ipsec_ops.create_ipsec_connection('ipsec', None, peer_address, '123456', vip1.uuid, None)
    except:
        test_util.test_fail('Failed to create vpc ipsec')


    ipsec_ops.attach_remote_cidr_to_ipsec_connection(peer_cidrs, ipsec_uuid)

    ipsec_ops.detach_remote_cidr_from_ipsec_connection(peer_cidrs, ipsec_uuid)

    test_util.test_pass('Attach Detach L3Network Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global ipsec
    if ipsec != None:
        ipsec_ops.delete_ipsec_connection(ipsec.uuid)

