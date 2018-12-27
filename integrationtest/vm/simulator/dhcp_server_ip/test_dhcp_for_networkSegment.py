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

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
	test_util.test_logger("start dhcp test for l3 public network")

	test_util.test_dsc("get no vlan network uuid")
	public_network = test_stub_dhcp.Public_Ip_For_Dhcp()
	public_network.set_l2_query_resource(res_ops.L2_NETWORK)
	public_network.set_l2_type("L2NoVlanNetwork")
	l2_no_vlan_uuid = public_network.getl2uuid()
	test_util.test_logger("antony @@@debug : %s" %(l2_no_vlan_uuid))
	test_util.test_logger("create l3 network")
