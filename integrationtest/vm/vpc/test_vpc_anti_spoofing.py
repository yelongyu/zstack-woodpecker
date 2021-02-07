'''
@author: Hengguo.Ge
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.config_operations as cfg_ops
import os
from itertools import izip

VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork2"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]
CLASSIC_L3 = 'l3NoVlanNetworkName2'

vpc1_l3_list = [VLAN1_NAME, VLAN2_NAME]
vpc2_l3_list = [VXLAN1_NAME, VXLAN2_NAME]

vpc_l3_list = [vpc1_l3_list, vpc2_l3_list]
vpc_name_list = ['vpc1','vpc2']

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vr_list = []


def test():

    test_util.test_dsc("set global config anti-spoofing value to true ")
    cfg_ops.change_global_config(category="vm", name="cleanTraffic", value="true")

    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(VLAN1_NAME, VLAN2_NAME))
    vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(VLAN1_NAME), l3_name=VLAN1_NAME)
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(VLAN2_NAME), l3_name=VLAN2_NAME)
    test_obj_dict.add_vm(vm2)
    vm2.check()

    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr_list[0].inv)

    test_util.test_dsc("Create vip")
    vip = test_stub.create_vip('vip1', vr_pub_nic.l3NetworkUuid)
    test_obj_dict.add_vip(vip)

    test_util.test_dsc("Create eip")
    eip = test_stub.create_eip('eip1', vip_uuid=vip.get_vip().uuid)
    vip.attach_eip(eip)
    vip.check()

    test_util.test_dsc("set global config anti-spoofing value to default value false ")
    cfg_ops.change_global_config(category="vm", name="cleanTraffic", value="false")

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
