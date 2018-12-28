'''
1.create public network with Network segment
2.check dhcp ip address

@author Antony WeiJiang
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import test_stub_for_dhcp_ip as test_stub_dhcp
import random

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
l2_query_resource = res_ops.L2_NETWORK
type_l2 = ["L2NoVlanNetwork","L2VlanNetwork"]
start_ip, endip = ("172.20.83.51","172.20.83.53")
gate_way = "172.20.0.1"
net_mask = "255.255.0.0"
l3_name = "test_dhcp_server"
ip_range_name = "dhcp_ip_range"
ip_Version = [4,6]
ip_range_for_public = [start_ip,"172.20.83.52",endip]
dhcp_system_tags = []
dhcp_ip_for_public = ip_range_for_public[random.randint(0,len(ip_range_for_public)-1)]

def test():
	test_util.test_logger("start dhcp test for l3 public network")

	test_util.test_dsc("get no vlan network uuid")
	public_network = test_stub_dhcp.Public_Ip_For_Dhcp()
	public_network.set_l2_query_resource(l2_query_resource)
	public_network.set_l2_type(type_l2[0])
	l2_no_vlan_uuid = public_network.get_l2uuid()
	test_util.test_logger("antony @@@debug : %s" %(l2_no_vlan_uuid))
	
	test_util.test_logger("create l3 network")
	public_network.create_l3uuid(l3_name)
	test_util.test_logger("antony @@@debug : %s" %(public_network.get_l3uuid()))

	test_util.test_logger("add ip v4 range to l3 network")
	public_network.add_ip_range(ip_range_name, start_ip, endip, gate_way, net_mask, ip_Version[0])
	
	
	
