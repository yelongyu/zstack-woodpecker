'''
@author: yixin.wang
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import random
import os
import time
from itertools import izip

DefaultFalseDict = test_lib.DefaultFalseDict

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vpc_ha_group_name_list = ['test_vpc_ha', 'test_vpc_ha_upgrade']
ha_group_vpc_name_list = ['vpc-test','vpc-test-peer']
ha_monitor_ip = ['192.168.0.1']
vpc_name_list = ['vpc1','vpc2']
vpc_l3_list = [test_stub.vpc1_l3_list, test_stub.vpc2_l3_list, test_stub.vpc3_l3_list]
vr_list = []
ha_vr_list = []
ha_group_list = []

case_flavor = dict(vr_only=             DefaultFalseDict(vr=True),
                   vr_attach_l3=        DefaultFalseDict(vr=True, attach_l3=True),
                   vr_attach_l3_has_vm= DefaultFalseDict(vr=True, attach_l3=True, has_vm=True)
                   )


@test_lib.pre_execution_action(test_stub.remove_all_vpc_ha_group)
@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)

def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    
    test_util.test_dsc("create vpc ha group and new vpc vrouter then attach l3 and create vm")
    for ha_group_name in vpc_ha_group_name_list:
        ha_group_list.append(test_stub.create_vpc_ha_group(ha_group_name, ha_monitor_ip))
    
    for ha_vpc_name in ha_group_vpc_name_list:
        ha_vr_list.append(test_stub.create_vpc_vrouter_with_tags(ha_vpc_name, tags='haUuid::{}'.format(ha_group_list[0].uuid)))
    time.sleep(10)
    test_stub.add_dns_to_ha_vpc(ha_vr_list[0].inv.uuid)

    if flavor["attach_l3"]:
        test_util.test_dsc("attach l3 to no_ha_vpc and ha_vpc vrouter")
        for vr, l3_list in izip(vr_list, vpc_l3_list):
            test_stub.attach_l3_to_vpc_vr(vr, l3_list)

        ha_vr = random.choice(ha_vr_list)
        l3_attach = random.choice(vpc_l3_list[2])
        test_stub.attach_l3_to_vpc_vr(ha_vr, [l3_attach])

    if flavor["has_vm"]:
        test_util.test_dsc("create vm with vpc l3")
        l3 = random.choice(test_stub.vpc1_l3_list + test_stub.vpc2_l3_list)
        vm = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(l3), l3_name=l3)
        test_obj_dict.add_vm(vm)
        vm.check()
    
        ha_vm = test_stub.create_vm_with_random_offering(vm_name='ha_vpc_vm_{}'.format(l3_attach), l3_name=l3_attach)
        test_obj_dict.add_vm(ha_vm)
        ha_vm.check()

    test_util.test_dsc("upgrade no_ha_vpc vrouter")
    vr_list[0].stop()
    vr_list[0].start_with_tags(tags='haUuid::{}'.format(ha_group_list[1].uuid))
    ha_vr_list.append(vr_list[0])
    ha_vr_list.append(test_stub.create_vpc_vrouter_with_tags(vr_name='{}-peer'.format(vpc_name_list[0]), \
        tags='haUuid::{}'.format(ha_group_list[1].uuid)))

    for ha_group in ha_group_list:
        while test_stub.check_ha_status(ha_group.uuid):
            print test_stub.check_ha_status(ha_group.uuid)
            break

    if flavor["has_vm"]:
        for ha_vr in ha_vr_list:
            ha_vr.destroy()
        
        for vr in vr_list:
            vr.destroy()

        with test_lib.expected_failure('reboot vm in vpc l3 when no vpc vrouter', Exception):
            vm.reboot()
            ha_vm.reboot()
    
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()






