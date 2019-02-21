'''
1.create private vpc router network with Network segment
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
type_l2 = ["L2NoVlanNetwork", "L2VlanNetwork"]
start_ip, endip = ("192.168.1.2", "192.168.1.4")
start_ip1, end_ip1 = ("192.168.1.5", "192.168.1.6")
gate_way = "192.168.1.1"
net_mask = "255.255.255.0"
l3_name = "test_dhcp_server"
ip_range_name = "dhcp_ip_range"
ip_Version = [4, 6]
ip_range_for_private_vpc = [start_ip, "192.168.1.3", endip]
ip_range_for_networksegment = [start_ip1, end_ip1]
dhcp_ip_for_private_vpc = ip_range_for_private_vpc[random.randint(
    0, len(ip_range_for_private_vpc) - 1)]
dhcp_system_tags = [
    "flatNetwork::DhcpServer::" +
    dhcp_ip_for_private_vpc +
    "::ipUuid::null"]


def test():
    test_util.test_logger("start dhcp test for l3 public network")

    test_util.test_dsc("get no vlan network uuid")
    private_vpcnetwork = test_stub_dhcp.VpcNetwork_IP_For_Dhcp()
    private_vpcnetwork.set_l2_query_resource(l2_query_resource)
    private_vpcnetwork.set_l2_type(type_l2[1])
    l2_no_vlan_uuid = private_vpcnetwork.get_l2uuid()
    test_util.test_logger("antony @@@debug : %s" % (l2_no_vlan_uuid))

    test_util.test_logger("create l3 network")
    private_vpcnetwork.set_ipVersion(ip_Version[0])
    private_vpcnetwork.create_l3uuid(l3_name)
    test_util.test_logger(
        "antony @@@debug : %s" %
        (private_vpcnetwork.get_l3uuid()))
    private_vpcnetwork.add_service_to_l3_vpcnetwork()

    test_util.test_logger("add ip v4 range to l3 network")
    private_vpcnetwork.add_ip_range(
        ip_range_name,
        start_ip,
        endip,
        gate_way,
        net_mask,
        dhcp_system_tags)
    if private_vpcnetwork.check_dhcp_ipaddress().find(dhcp_ip_for_private_vpc) == -1:
        test_util.test_fail("dhcp server ip create fail")

    test_util.test_logger("add extra networksegment")
    private_vpcnetwork.add_ip_range(
        ip_range_name,
        start_ip1,
        end_ip1,
        gate_way,
        net_mask)

    test_util.test_logger("crete vpc vrouter")
    vm_object = test_stub_dhcp.Create_Vm_Instance()
    vm_object.create_vpc_vrouter()
    net_ops.attach_l3(
        private_vpcnetwork.get_l3uuid(),
        vm_object.get_vr_inv().uuid)

    list_vm = []
    for i in range(0, len(ip_range_for_private_vpc) +
                   len(ip_range_for_networksegment) - 1):
        list_vm.append(vm_object.create_vm(private_vpcnetwork.get_l3uuid()))

    try:
        vm_object.create_vm(private_vpcnetwork.get_l3uuid())
    except BaseException:
        test_util.test_logger("Catch expected exception,try to delete vm")

        test_util.test_logger("delete vm")
        for vm in list_vm:
            vm.clean()
        test_util.test_logger("delete l3 network")
        private_vpcnetwork.del_l3uuid()
        vm_object.delete_vpc_vrouter()
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
