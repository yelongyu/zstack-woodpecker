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


VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork2"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]
CLASSIC_L3 = 'l3NoVlanNetworkName2'

vpc1_l3_list = [VLAN1_NAME, VLAN2_NAME]
vpc2_l3_list = [VXLAN1_NAME, VXLAN2_NAME]

vpc_l3_list = [vpc1_l3_list, vpc2_l3_list]

vpc_name_list =['vpc1', 'vpc2']
new_vpc_name_list =['vpc11', 'vpc22']
ha_group_name_list=['vpc-ha-1','vpc-ha-2']
new_ha_group_name_list=['vpc-ha-11','vpc-ha-22']
ha_group_list = []
new_ha_group_list = []

case_flavor = dict(vm1_vm2_one_vpc_1vlan=   dict(vm1l3=VLAN1_NAME, vm2l3=VLAN1_NAME),
                   vm1_vm2_one_vpc_2vlan=   dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME),
                   vm1_vm2_two_vpc=         dict(vm1l3=VLAN1_NAME, vm2l3=VXLAN2_NAME),
                   vm1_classic_vm2_vpc  =   dict(vm1l3=CLASSIC_L3, vm2l3=VXLAN2_NAME)
                   )

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vr_list= []
new_vr_list= []

def create_eip_and_vip():
    global vm1,vm2,vip_list,vr_list
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr_list[0].inv)
    vip_list = []
    for vm in (vm1, vm2):
        test_util.test_dsc("Create vip for vm {}".format(vm.get_vm().name))
        vip = test_stub.create_vip('vip_{}'.format(vm.get_vm().name), vr_pub_nic.l3NetworkUuid)
        vip_list.append(vip)
        test_util.test_dsc("Create eip for vm {}".format(vm.get_vm().name))
        eip = test_stub.create_eip('eip_{}'.format(vm.get_vm().name), vip_uuid=vip.get_vip().uuid)
        vip.attach_eip(eip)
        eip.attach(vm.get_vm().vmNics[0].uuid, vm)
        time.sleep(10)  
        # vip.check()   ##vpc_ha can not check tcp by vip.
    for vm in (vm1, vm2):
        vm.check()

def test_vm_connection():
    global vm1,vm2,vip_list,vr_list
    vm1_inv, vm2_inv = [vm.get_vm() for vm in (vm1, vm2)]
    vip1, vip2 = vip_list

    test_util.test_dsc("test two vm EIP connectivity")
    test_stub.run_command_in_vm(vm1_inv, 'iptables -F')
    test_stub.run_command_in_vm(vm2_inv, 'iptables -F')

    test_lib.lib_check_ping(vm1_inv, vip2.get_vip().ip)
    test_lib.lib_check_ping(vm2_inv, vip1.get_vip().ip)

    test_lib.lib_check_ports_in_a_command(vm1_inv, vip1.get_vip().ip,vip2.get_vip().ip, ["22"], [], vm2_inv)
    test_lib.lib_check_ports_in_a_command(vm2_inv, vip2.get_vip().ip,vip1.get_vip().ip, ["22"], [], vm1_inv)

def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()
    global vm1,vm2,vip_list,vr_list
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(flavor['vm1l3'], flavor['vm2l3']))
    vm1, vm2 = [test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(name), l3_name=name) for name in (flavor['vm1l3'], flavor['vm2l3'])]
    [test_obj_dict.add_vm(vm) for vm in (vm1,vm2)]
    [vm.check() for vm in (vm1,vm2)]

    create_eip_and_vip()
    test_vm_connection()

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

    test_vm_connection()

    test_lib.lib_error_cleanup(test_obj_dict)
    for vip in vip_list:
        vip.delete()
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

    test_util.test_dsc("add DNS and l3")
    for vr in new_vr_list:
        test_stub.add_dns_to_ha_vpc(vr.inv.uuid)
    for vr, l3_list in izip(new_vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(flavor['vm1l3'], flavor['vm2l3']))
    vm1, vm2 = [test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(name), l3_name=name) for name in (flavor['vm1l3'], flavor['vm2l3'])]
    [test_obj_dict.add_vm(vm) for vm in (vm1,vm2)]
    [vm.check() for vm in (vm1,vm2)]

    vr_list = new_vr_list
    create_eip_and_vip()
    test_vm_connection()

    test_util.test_dsc("change vpc vr ha status ")
    for ha_group in new_ha_group_list:
        test_stub.update_ha_status(ha_group.uuid)

    test_vm_connection()

    test_lib.lib_error_cleanup(test_obj_dict)
    for vip in vip_list:
        vip.delete()
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    for vip in vip_list:
        vip.delete()
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()