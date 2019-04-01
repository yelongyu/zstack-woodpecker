'''
@author: Hengguo Ge
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vpc_operations as vpc_ops
import os
import time
from itertools import izip

VPC1_VLAN, VPC1_VXLAN = ['l3VlanNetwork2', "l3VxlanNetwork12"]
VPC2_VLAN, VPC2_VXLAN = ["l3VlanNetwork3", "l3VxlanNetwork13"]

vpc_l3_list = [(VPC1_VLAN, VPC1_VXLAN), (VPC2_VLAN, VPC2_VXLAN)]

vpc_name_list = ['vpc1', 'vpc2']

case_flavor = dict(vm1_l3_vlan_vm2_l3_vlan=dict(vm1l3=VPC1_VLAN, vm2l3=VPC2_VLAN),
                   vm1_l3_vxlan_vm2_l3_vxlan=dict(vm1l3=VPC1_VXLAN, vm2l3=VPC2_VXLAN),
                   vm1_l3_vlan_vm2_l3_vxlan=dict(vm1l3=VPC1_VLAN, vm2l3=VPC2_VXLAN),
                   )

ospf_area_id = '0.0.0.0'
ospf_area_type = 'Standard'

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vr_list = []
vpc1_l3_uuid = []
vpc2_l3_uuid = []
vr_uuid = []
public_net = 'public network'


def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    for vpc1_l3 in vpc_l3_list[0]:
        vpc1_l3_uuid.append(test_lib.lib_get_l3_by_name(vpc1_l3).uuid)
    for vpc2_l3 in vpc_l3_list[1]:
        vpc2_l3_uuid.append(test_lib.lib_get_l3_by_name(vpc2_l3).uuid)

    vpc1_l3_uuid.append(test_lib.lib_get_l3_by_name(public_net).uuid)
    vpc2_l3_uuid.append(test_lib.lib_get_l3_by_name(public_net).uuid)

    vm1, vm2 = [test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(name), l3_name=name) for name in
                (flavor['vm1l3'], flavor['vm2l3'])]

    [test_obj_dict.add_vm(vm) for vm in (vm1, vm2)]
    [vm.check() for vm in (vm1, vm2)]

    [test_stub.run_command_in_vm(vm.get_vm(), 'iptables -F') for vm in (vm1, vm2)]

    test_util.test_dsc("disable snat before create ospf")
    for vr in vr_list:
        vpc_ops.set_vpc_vrouter_network_service_state(vr.inv.uuid, networkService='SNAT', state='disable')

    test_util.test_dsc("test vm1 and vm2 connectivity without ospf")
    test_stub.check_icmp_between_vms(vm1, vm2, expected_result='FAIL')

    test_util.test_dsc("create ospf")
    vpc_ops.create_vrouter_ospf_area(areaId=ospf_area_id, areaType=ospf_area_type)
    area_uuid = test_lib.lib_get_ospf_area_by_area_id(areaId=ospf_area_id).uuid

    test_util.test_dsc("add vpc to ospf")
    for vr in vr_list:
        vr_uuid.append(vr.inv.uuid)

    for vpc_l3 in vpc1_l3_uuid:
        vpc_ops.add_vrouter_networks_to_ospf_area(vr_uuid[0], [vpc_l3], area_uuid)
    for vpc_l3 in vpc2_l3_uuid:
        vpc_ops.add_vrouter_networks_to_ospf_area(vr_uuid[1], [vpc_l3], area_uuid)

    time.sleep(60)
    '''
    test_util.test_dsc("check ospf neighbor state")
    for vr in vr_uuid:
        if 'Full' not in vpc_ops.get_vrouter_ospf_neighbor(vr).state:
            test_util.test_fail('cannot form ospf neighbor, test fail')
    '''
    test_util.test_dsc("test vm1 and vm2 connectivity with ospf")
    test_stub.check_icmp_between_vms(vm1, vm2, expected_result='PASS')

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
    vpc_ops.delete_vrouter_ospf_area(area_uuid)


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()