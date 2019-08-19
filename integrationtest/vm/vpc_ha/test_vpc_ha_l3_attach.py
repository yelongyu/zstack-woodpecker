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

vpc_name_list = ['vpc1']
vpc_l3_list = [test_stub.vpc1_l3_list, test_stub.vpc2_l3_list]
vr_list = []
ha_group_name_list = ['vpc-ha-1']
ha_group_list = []
group_vr_list = []

@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
@test_lib.pre_execution_action(test_stub.remove_all_vpc_ha_group)

def test():
    test_util.test_dsc("Create a vpc ha group and a vpc vrouter , attach the same l3network to them.")
    for ha_group in ha_group_name_list:
        ha_group_list.append(test_stub.create_vpc_ha_group(ha_group_name = ha_group))
        # test_util.test_logger(ha_group_list[i].uuid)
        group_vr_list.append(test_stub.create_vpc_vrouter_with_tags(vr_name=vpc_name_list[0],tags='haUuid::{}'.format(ha_group_list[0].uuid)))
        vr_list.append(test_stub.create_vpc_vrouter_with_tags(vr_name=vpc_name_list[0]+'-peer',tags='haUuid::{}'.format(ha_group_list[0].uuid)))

    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vr_name = vpc_name))
     
    l3_uuid = test_lib.lib_get_l3_by_name('l3VlanNetwork10').uuid

    test_stub.attach_l3_to_vpc_vr_by_uuid(group_vr_list[0], l3_uuid)
    test_util.test_logger(" The operation is successful.")

    error = 0
    pa = 0
    for vpc_vr in vr_list:
        try:
            test_stub.attach_l3_to_vpc_vr_by_uuid(vpc_vr,l3_uuid )
        except Exception as e:
            test_util.test_logger("The vpc l3 was already attached")
            error += 1
        else:
            test_util.test_logger(" The operation is successful.")
            pa += 1

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