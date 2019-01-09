'''
1.create private vpc router network with cidr
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
l3_name = "test_dhcp_server"
ip_range_name = "dhcp_ip_range"
ip_Version = [4,6]
networkcidr = "192.168.1.0/24"
dhcp_ip_for_private_vpc = "192.168.1.3"
dhcp_system_tags = ["flatNetwork::DhcpServer::"+dhcp_ip_for_private_vpc+"::ipUuid::null"]

def test():
	test_util.test_logger("start dhcp test for l3 public network")

	test_util.test_dsc("get no vlan network uuid")
	private_vpcnetwork = test_stub_dhcp.VpcNetwork_IP_For_Dhcp()
	private_vpcnetwork.set_l2_query_resource(l2_query_resource)
	private_vpcnetwork.set_l2_type(type_l2[1])
	l2_no_vlan_uuid = private_vpcnetwork.get_l2uuid()
	test_util.test_logger("antony @@@debug : %s" %(l2_no_vlan_uuid))
	
	test_util.test_logger("create l3 network")
	private_vpcnetwork.set_ipVersion(ip_Version[0])
	private_vpcnetwork.create_l3uuid(l3_name)
	test_util.test_logger("antony @@@debug : %s" %(private_vpcnetwork.get_l3uuid()))
	private_vpcnetwork.add_service_to_l3_vpcnetwork()

	test_util.test_logger("add ip v4 range to l3 network")
	private_vpcnetwork.add_ip_by_networkcidr(ip_range_name, networkcidr, dhcp_system_tags)
	if private_vpcnetwork.check_dhcp_ipaddress().find(dhcp_ip_for_private_vpc) == -1:
		test_util.test_fail("dhcp server ip create fail")
	test_util.test_logger("delete l3 network")
	private_vpcnetwork.del_l3uuid()
	test_util.test_pass("dhcp server ip create successfully")

'''
to be define
'''
def error_cleanup():
	pass
'''
to be define
'''
def env_recover():
	pass

