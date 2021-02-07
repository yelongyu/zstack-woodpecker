'''
@author: Hengtao.Ran
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.host_operations as host_ops
import random
import time
import os
import zstackwoodpecker.operations.volume_operations as vol_ops
import time
from itertools import izip


VPC1_VLAN , VPC1_VXLAN = ['l3VlanNetwork2', "l3VxlanNetwork12"]
VPC2_VLAN, VPC2_VXLAN = ["l3VlanNetwork3", "l3VxlanNetwork13"]

vpc_l3_list = [(VPC1_VLAN , VPC1_VXLAN), (VPC2_VLAN, VPC2_VXLAN)]

vpc_name_list =['vpc1', 'vpc2']
new_vpc_name_list =['vpc11', 'vpc22']
ha_group_name_list=['vpc-ha-1','vpc-ha-2']
new_ha_group_name_list=['vpc-ha-11','vpc-ha-22']
ha_group_list = []
new_ha_group_list = []

case_flavor = dict(vm1_l3_vlan_vm2_l3_vlan=           dict(vm1l3=VPC1_VLAN, vm2l3=VPC2_VLAN),
                   vm1_l3_vxlan_vm2_l3_vxlan=         dict(vm1l3=VPC1_VXLAN, vm2l3=VPC2_VXLAN),
                   vm1_l3_vlan_vm2_l3_vxlan=          dict(vm1l3=VPC1_VLAN, vm2l3=VPC2_VXLAN),
                   )

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vr_list= []
new_vr_list= []

@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
@test_lib.pre_execution_action(test_stub.remove_all_vpc_ha_group)
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    vm1, vm2 = [test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(name), l3_name=name) for name in (flavor['vm1l3'], flavor['vm2l3'])]

    [test_obj_dict.add_vm(vm) for vm in (vm1,vm2)]
    [vm.check() for vm in (vm1,vm2)]

    test_util.test_dsc("test two vm connectivity")
    [test_stub.run_command_in_vm(vm.get_vm(), 'iptables -F') for vm in (vm1,vm2)]

    test_stub.check_icmp_between_vms(vm1, vm2, expected_result='FAIL')
    test_stub.check_tcp_between_vms(vm1, vm2, [], ["22"])

    test_util.test_dsc("create vpc ha group")
    for ha_group_name in ha_group_name_list:
        ha_group_list.append(test_stub.create_vpc_ha_group(ha_group_name = ha_group_name))
        
    test_util.test_dsc("add vpc vrouter into ha group")
    i = 0
    for ha_group in ha_group_list:
        vr_list[i].stop()
        vr_list[i].check()
        vr_list[i].start_with_tags(tags='haUuid::{}'.format(ha_group.uuid))
        test_stub.create_vpc_vrouter_with_tags(vr_name=vpc_name_list[i]+'-peer',tags='haUuid::{}'.format(ha_group.uuid))
        test_stub.check_ha_status(ha_group.uuid)
        i += 1

    test_util.test_dsc("test two vm connectivity")
    [test_stub.run_command_in_vm(vm.get_vm(), 'iptables -F') for vm in (vm1,vm2)]

    test_stub.check_icmp_between_vms(vm1, vm2, expected_result='FAIL')
    test_stub.check_tcp_between_vms(vm1, vm2, [], ["22"])
    
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()

    test_util.test_dsc("create vpc ha group")
    for ha_group_name in new_ha_group_name_list:
        new_ha_group_list.append(test_stub.create_vpc_ha_group(ha_group_name = ha_group_name))
        
    test_util.test_dsc("add vpc vrouter into ha group")
    i = 0
    for ha_group in new_ha_group_list:
        new_vr_list.append(test_stub.create_vpc_vrouter_with_tags(vr_name=new_vpc_name_list[i],tags='haUuid::{}'.format(ha_group.uuid))) 
        test_stub.create_vpc_vrouter_with_tags(vr_name=new_vpc_name_list[i]+'-peer',tags='haUuid::{}'.format(ha_group.uuid))
        test_stub.check_ha_status(ha_group.uuid)
        i += 1

    test_util.test_dsc("add DNS ")
    for vr in new_vr_list:
        test_stub.add_dns_to_ha_vpc(vr.inv.uuid)

    test_util.test_dsc("add l3 ")
    for vr, l3_list in izip(new_vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    vm11, vm22 = [test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(name), l3_name=name) for name in (flavor['vm1l3'], flavor['vm2l3'])]

    [test_obj_dict.add_vm(vm) for vm in (vm11,vm22)]
    [vm.check() for vm in (vm11,vm22)]

    test_util.test_dsc("test two vm connectivity")
    [test_stub.run_command_in_vm(vm.get_vm(), 'iptables -F') for vm in (vm11,vm22)]

    test_stub.check_icmp_between_vms(vm11, vm22, expected_result='FAIL')
    test_stub.check_tcp_between_vms(vm11, vm22, [], ["22"])

    test_util.test_dsc("change vpc vr ha status ")
    for ha_group in new_ha_group_list:
        test_stub.update_ha_status(ha_group.uuid)

    test_util.test_dsc("test two vm connectivity")
    [test_stub.run_command_in_vm(vm.get_vm(), 'iptables -F') for vm in (vm11,vm22)]

    test_stub.check_icmp_between_vms(vm11, vm22, expected_result='FAIL')
    test_stub.check_tcp_between_vms(vm11, vm22, [], ["22"])

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()
