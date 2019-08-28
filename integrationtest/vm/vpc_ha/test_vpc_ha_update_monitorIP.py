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





monitorIp_list = ['1.1.1.1','2.2.2.2']

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

all_vr_list = []

@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
@test_lib.pre_execution_action(test_stub.remove_all_vpc_ha_group)
def test():
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))

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
    
    i = 0
    for ha_group in ha_group_list:
    	test_stub.update_ha_group_monitorip(ha_group.uuid, monitorIp=[monitorIp_list[i]])
    	i += 1

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

    i = 0
    for ha_group in new_ha_group_list:
    	test_stub.update_ha_group_monitorip(ha_group.uuid, monitorIp=[monitorIp_list[i]])
    	i += 1

    test_util.test_dsc("change vpc vr ha status ")
    for ha_group in new_ha_group_list:
        test_stub.update_ha_status(ha_group.uuid)
        test_stub.check_ha_status(ha_group.uuid)

    i = 0
    for ha_group in new_ha_group_list:
    	test_stub.update_ha_group_monitorip(ha_group.uuid, monitorIp=['6.6.6.6'])
    	i += 1

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()
