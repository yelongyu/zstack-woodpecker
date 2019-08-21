'''
@author: Hengtao.Ran
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import random
import os
from itertools import izip
DefaultFalseDict = test_lib.DefaultFalseDict

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vpc_name_list = ['vpc1','vpc2']
vr_list = []
ha_group_name_list = ['vpc-ha-1']
ha_group_list = []

@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
@test_lib.pre_execution_action(test_stub.remove_all_vpc_ha_group)
def test():
    test_util.test_dsc("Create a vpc ha group and a vpc vrouter , attach the same l3network to them.")
    ha_group_list.append(test_stub.create_vpc_ha_group(ha_group_name = ha_group_name_list[0]))
        
    vr_list.append(test_stub.create_vpc_vrouter(vr_name = vpc_name_list[0]))
     
    vr_list[0].stop()
    vr_list[0].start_with_tags(tags='haUuid::{}'.format(ha_group_list[0].uuid))
    test_stub.create_vpc_vrouter_with_tags(vr_name=vpc_name_list[0]+'-peer',tags='haUuid::{}'.format(ha_group_list[0].uuid))
    test_util.test_logger("=========start_with_tags========")

    
    vr_list[0].reboot()
    vr_list[0].check()
    test_util.test_logger("=========reboot========")

    vr_list[0].destroy()
    vr_list[0].check()
    
    vr_list.append(test_stub.create_vpc_vrouter_with_tags(vr_name=vpc_name_list[1],tags='haUuid::{}'.format(ha_group_list[0].uuid)))
    test_util.test_logger("=========add vr again.========")

    test_lib.lib_error_cleanup(test_obj_dict)
    # test_stub.remove_all_vpc_vrouter()
    for vm in vr_list:
        vm.destroy()
    test_stub.remove_all_vpc_ha_group()
    

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    # test_stub.remove_all_vpc_vrouter()
    for vm in vr_list:
        vm.destroy()
    test_stub.remove_all_vpc_ha_group()