'''
@author: Hengtao.Ran
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vpc_operations as vpc_ops
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

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vr_list= []
new_vr_list= []

def check_snat_state():
    global vr_list
    test_util.test_dsc("check snat state")
    for vr in vr_list:
        vr_uuid = vr.inv.uuid
        try:
            vpc_ops.get_vpc_vrouter_network_service_state(vr_uuid) == 'enable'
        except Exception as e:
            raise e

        vpc_ops.set_vpc_vrouter_network_service_state(vr_uuid, networkService='SNAT', state='disable')
        try:
            vpc_ops.get_vpc_vrouter_network_service_state(vr_uuid) == 'disable'
        except Exception as e:
            raise e

def test():
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()
    global vr_list
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    check_snat_state()

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

    check_snat_state()

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

    vr_list = new_vr_list
    check_snat_state()

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()
 
def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()