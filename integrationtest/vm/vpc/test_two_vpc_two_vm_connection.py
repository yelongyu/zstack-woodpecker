'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.host_operations as host_ops
import random
import os
import zstackwoodpecker.operations.volume_operations as vol_ops
import time
from itertools import izip


VPC1_VLAN , VPC1_VXLAN = ['l3VlanNetwork2', "l3VxlanNetwork12"]
VPC2_VLAN, VPC2_VXLAN = ["l3VlanNetwork3", "l3VxlanNetwork13"]

vpc_l3_list = [(VPC1_VLAN , VPC1_VXLAN), (VPC2_VLAN, VPC2_VXLAN)]

vpc_name_list =['vpc1', 'vpc2']


case_flavor = dict(vm1_l3_vlan_vm2_l3_vlan=           dict(vm1l3=VPC1_VLAN, vm2l3=VPC2_VLAN),
                   vm1_l3_vxlan_vm2_l3_vxlan=         dict(vm1l3=VPC1_VXLAN, vm2l3=VPC2_VXLAN),
                   vm1_l3_vlan_vm2_l3_vxlan=          dict(vm1l3=VPC1_VLAN, vm2l3=VPC2_VXLAN),
                   )


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vr_list= []


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

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
