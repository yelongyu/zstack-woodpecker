'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import apibinding.inventory as inventory
from itertools import izip
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops


VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork2"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]
SECOND_PUB = 'l3NoVlanNetworkName1'

vpc1_l3_list = [VLAN1_NAME, VLAN2_NAME, SECOND_PUB]
vpc2_l3_list = [VXLAN1_NAME, VXLAN2_NAME, SECOND_PUB]

vpc_l3_list = [vpc1_l3_list, vpc2_l3_list]
vpc_name_list = ['vpc1', 'vpc2']

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vr_list =[]


def test():
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    vr1, vr2 = vr_list

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(VLAN1_NAME, VXLAN1_NAME))
    vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(VLAN1_NAME), l3_name=VLAN1_NAME)
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(VXLAN1_NAME), l3_name=VXLAN1_NAME)
    test_obj_dict.add_vm(vm2)
    vm2.check()

    cond = res_ops.gen_query_conditions('name', '=', os.environ.get(SECOND_PUB))
    second_pub_l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]

    test_util.test_dsc("Create vroute route for vpc1")
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get(VXLAN1_NAME))
    vpc2_l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    vpc2_l3_cdir = vpc2_l3.ipRanges[0].networkCidr
    vpc2_second_pub_ip = [nic.ip for nic in vr2.inv.vmNics if nic.l3NetworkUuid == second_pub_l3.uuid][0]

    route_table1 = net_ops.create_vrouter_route_table('vpc1')
    route_entry1 = net_ops.add_vrouter_route_entry(route_table1.uuid, vpc2_l3_cdir, vpc2_second_pub_ip)
    net_ops.attach_vrouter_route_table_to_vrouter(route_table1.uuid, vr1.inv.uuid)

    test_util.test_dsc("Create vroute route for vpc2")
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get(VLAN1_NAME))
    vpc1_l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    vpc1_l3_cdir = vpc1_l3.ipRanges[0].networkCidr
    vpc1_second_pub_ip = [nic.ip for nic in vr1.inv.vmNics if nic.l3NetworkUuid == second_pub_l3.uuid][0]

    route_table2 = net_ops.create_vrouter_route_table('vpc2')
    route_entry1 = net_ops.add_vrouter_route_entry(route_table2.uuid, vpc1_l3_cdir, vpc1_second_pub_ip)
    net_ops.attach_vrouter_route_table_to_vrouter(route_table2.uuid, vr2.inv.uuid)

    vm1_inv, vm2_inv = [vm.get_vm() for vm in (vm1, vm2)]

    test_lib.lib_check_ping(vm1_inv, vm2_inv.vmNics[0].ip)
    test_lib.lib_check_ping(vm2_inv, vm1_inv.vmNics[0].ip)

    test_lib.lib_check_ports_in_a_command(vm1_inv, vm1_inv.vmNics[0].ip,
                                          vm2_inv.vmNics[0].ip, ["22"], [], vm2_inv)

    test_lib.lib_check_ports_in_a_command(vm2_inv, vm2_inv.vmNics[0].ip,
                                          vm1_inv.vmNics[0].ip, ["22"], [], vm1_inv)

    net_ops.detach_vrouter_route_table_from_vrouter(route_table1.uuid, vr1.inv.uuid)
    net_ops.detach_vrouter_route_table_from_vrouter(route_table2.uuid, vr2.inv.uuid)

    with test_lib.expected_failure('Check two vm pingable', Exception):
        test_lib.lib_check_ping(vm1_inv, vm2_inv.vmNics[0].ip)

    with test_lib.expected_failure('Check two vm pingable', Exception):
        test_lib.lib_check_ping(vm2_inv, vm1_inv.vmNics[0].ip)

    test_lib.lib_check_ports_in_a_command(vm1_inv, vm1_inv.vmNics[0].ip,
                                          vm2_inv.vmNics[0].ip, [], ["22"], vm2_inv)

    test_lib.lib_check_ports_in_a_command(vm2_inv, vm2_inv.vmNics[0].ip,
                                          vm1_inv.vmNics[0].ip, [], ["22"], vm1_inv)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

