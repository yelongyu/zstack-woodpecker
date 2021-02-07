'''
1.create public network with Network segment
	1.1 add ipv6 address
2.check dhcp ip address
3.add extra networksegment ipv6
4.create vm to use ip

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
type_l2 = ["L2NoVlanNetwork", "L2VlanNetwork"]
start_ip, endip = ("CDCD:910A:2222:5498:8475:1111:3900:2020",
                   "CDCD:910A:2222:5498:8475:1111:3900:2022")
start_ip1, endip1 = ("CDCD:910A:2222:5498:8475:1111:3900:2024",
                     "CDCD:910A:2222:5498:8475:1111:3900:2025")
gate_way = "CDCD:910A:2222:5498:8475:1111:3900:2023"
prifixLen = 120
l3_name = "test_dhcp_server"
ip_range_name = "dhcp_ip_range"
ip_Version = [4, 6]
ip_range_for_public = [
    start_ip, "CDCD:910A:2222:5498:8475:1111:3900:2021", endip
]
ip_range_for_networksegment = [start_ip1, endip1]
dhcp_ip_for_public = ip_range_for_public[random.randint(
    0, len(ip_range_for_public)-1
)]
dhcp_system_tags = ["flatNetwork::DhcpServer::" + dhcp_ip_for_public+"::ipUuid::null"]


def test():
    test_util.test_logger("start dhcp test for l3 public network")

    test_util.test_dsc("get no vlan network uuid")
    public_network = test_stub_dhcp.Public_Ip_For_Dhcp()
    public_network.set_l2_query_resource(l2_query_resource)
    public_network.set_l2_type(type_l2[0])
    l2_no_vlan_uuid = public_network.get_l2uuid()

    test_util.test_logger("create l3 network")
    public_network.set_ipVersion(ip_Version[1])
    public_network.create_l3uuid(l3_name)
    public_network.add_service_to_l3network()

    test_util.test_logger("add ip v4 range to l3 network")
    public_network.add_ipv6_range(ip_range_name, start_ip, endip, gate_way, prifixLen, dhcp_system_tags
                                  )

    if public_network.check_dhcp_ipaddress().find(dhcp_ip_for_public.lower()) == -1:
        test_util.test_fail("dhcp server ip create fail")

    test_util.test_logger("add extra networksegment")
    public_network.add_ipv6_range(
        ip_range_name, start_ip1, endip1, gate_way, prifixLen
    )

    test_util.test_logger("add vm install")
    vm_object = test_stub_dhcp.Create_Vm_Instance()
    list_vm = []
    for i in range(0, len(ip_range_for_public)+len(ip_range_for_networksegment)-1):
        list_vm.append(vm_object.create_vm(public_network.get_l3uuid()))

    try:
        vm_object.create_vm(public_network.get_l3uuid())
    except:
        test_util.test_logger("Catch expected exception,try to delete vm")

        test_util.test_logger("delete vm")
        for vm in list_vm:
            vm.clean()
        test_util.test_logger("delete l3 network")
        public_network.del_l3uuid()
        test_util.test_pass("test dhcp server pass")

    test_util.test_fail("dhcp server ip create successfully")


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
