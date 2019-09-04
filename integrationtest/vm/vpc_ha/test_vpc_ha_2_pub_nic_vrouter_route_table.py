'''
@author: Hengtao.Ran
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
ha_group_name_list = ['vpc-ha-1','vpa-ha-2']
new_vpc_name_list = ['vpc11', 'vpc22']
new_ha_group_name_list = ['vpc-ha-11','vpa-ha-22']

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vr_list =[]
ha_group_list = []
table_list = []

new_vr_list =[]
new_ha_group_list = []

def create_vroute_table():
    global vr1, vr2,vr1_name,vr2_name,vm1,vm2,route_table1,route_table2,table_list
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get(SECOND_PUB))
    second_pub_l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]

    test_util.test_dsc("Create vroute route for {}".format(vr1_name))
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get(VXLAN1_NAME))
    vpc2_l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    vpc2_l3_cdir = vpc2_l3.ipRanges[0].networkCidr
    vpc2_second_pub_ip = [nic.ip for nic in vr2.inv.vmNics if nic.l3NetworkUuid == second_pub_l3.uuid][0]

    route_table1 = net_ops.create_vrouter_route_table(vr1_name)
    table_list.append(route_table1)
    route_entry1 = net_ops.add_vrouter_route_entry(route_table1.uuid, vpc2_l3_cdir, vpc2_second_pub_ip)
    net_ops.attach_vrouter_route_table_to_vrouter(route_table1.uuid, vr1.inv.uuid)

    test_util.test_dsc("Create vroute route for {}".format(vr2_name))
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get(VLAN1_NAME))
    vpc1_l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    vpc1_l3_cdir = vpc1_l3.ipRanges[0].networkCidr
    vpc1_second_pub_ip = [nic.ip for nic in vr1.inv.vmNics if nic.l3NetworkUuid == second_pub_l3.uuid][0]

    route_table2 = net_ops.create_vrouter_route_table(vr2_name)
    table_list.append(route_table2)
    route_entry1 = net_ops.add_vrouter_route_entry(route_table2.uuid, vpc1_l3_cdir, vpc1_second_pub_ip)
    net_ops.attach_vrouter_route_table_to_vrouter(route_table2.uuid, vr2.inv.uuid)

def vm_connection_test():
    global vr1, vr2,vr1_name,vr2_name,vm1,vm2,route_table1,route_table2,table_list
    vm1_inv, vm2_inv = [vm.get_vm() for vm in (vm1, vm2)]

    test_lib.lib_check_ping(vm1_inv, vm2_inv.vmNics[0].ip)
    test_lib.lib_check_ping(vm2_inv, vm1_inv.vmNics[0].ip)

    test_lib.lib_check_ports_in_a_command(vm1_inv, vm1_inv.vmNics[0].ip,vm2_inv.vmNics[0].ip, ["22"], [], vm2_inv)
    test_lib.lib_check_ports_in_a_command(vm2_inv, vm2_inv.vmNics[0].ip,vm1_inv.vmNics[0].ip, ["22"], [], vm1_inv)

def test():
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()
    global vr1, vr2,vr1_name,vr2_name,vm1,vm2,route_table1,route_table2,table_list
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(VLAN1_NAME, VXLAN1_NAME))
    vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(VLAN1_NAME), l3_name=VLAN1_NAME)
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(VXLAN1_NAME), l3_name=VXLAN1_NAME)
    test_obj_dict.add_vm(vm2)
    vm2.check()

    vr1, vr2 = vr_list
    vr1_name, vr2_name = vpc_name_list

    create_vroute_table()
    vm_connection_test()
    
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

    vm_connection_test()
 
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()
    for table in table_list:
        net_ops.delete_vrouter_route_table(table.uuid)
 
    table_list=[]
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

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(VLAN1_NAME, VXLAN1_NAME))
    vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(VLAN1_NAME), l3_name=VLAN1_NAME)
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(VXLAN1_NAME), l3_name=VXLAN1_NAME)
    test_obj_dict.add_vm(vm2)
    vm2.check()

    vr1, vr2 = new_vr_list
    vr1_name,vr2_name = new_vpc_name_list

    create_vroute_table()
    vm_connection_test()

    test_util.test_dsc("change vpc vr ha status ")
    for ha_group in new_ha_group_list:
        test_stub.update_ha_status(ha_group.uuid)

    vm_connection_test()

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()
    for table in table_list:
        net_ops.delete_vrouter_route_table(table.uuid)

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()
    for table in table_list:
        net_ops.delete_vrouter_route_table(table.uuid)