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
ha_group_name_list = ['vpc-ha-1','vpc-ha-2']
ha_group_list = []
group_vr_list = []

@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
@test_lib.pre_execution_action(test_stub.remove_all_vpc_ha_group)
def test():
    test_util.test_dsc("Create a vpc ha group with one vr and add a vr into group.")
    i = 0
    for ha_group in ha_group_name_list:
        ha_group_list.append(test_stub.create_vpc_ha_group(ha_group_name = ha_group))
        # test_util.test_logger(ha_group_list[i].uuid)
        group_vr_list.append(test_stub.create_vpc_vrouter_with_tags(vr_name=vpc_name_list[i]+'-peer',tags='haUuid::{}'.format(ha_group_list[i].uuid)))
        i += 1
        
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vr_name = vpc_name))
    
    num = 0
    error = 0
    for vr_name in vr_list:
        vr_name.stop()
        try:
            vr_name.start_with_tags(tags='haUuid::{}'.format(ha_group_list[num].uuid))
        except Exception as e:
            test_util.test_logger("This operation is not allowed")
            error += 1
        num += 1
    try:
            error == 2
    except Exception as e:
            raise
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