'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import random
import os
from itertools import izip



test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vpc1_l3_list = ['l3VlanNetworkName1', "l3VlanNetwork2", "l3VxlanNetwork11", "l3VxlanNetwork12"]
vpc3_l3_list = ['l3VlanNetwork3', "l3VlanNetwork4", "l3VxlanNetwork13", "l3VxlanNetwork14"]
vpc3_l3_list = ['l3VlanNetwork5', "l3VlanNetwork6", "l3VxlanNetwork15", "l3VxlanNetwork16"]

vpc_name_list = ['vpc1','vpc2','vpc3']
vpc_l3_list = [vpc1_l3_list, vpc3_l3_list, vpc3_l3_list]
vr_inv_list = []

case_flavor = dict(vr_only=             dict(vr=True, attach_l3=False, has_vm=False),
                   vr_attach_l3=        dict(vr=True, attach_l3=True, has_vm=False),
                   vr_attach_l3_has_vm= dict(vr=True, attach_l3=True, has_vm=True)
                   )


@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")

    for vpc_name in vpc_name_list:
        vr_inv_list.append(test_stub.create_vpc_vrouter(vpc_name))

    if flavor["attach_l3"]:
        for vr_inv, l3_list in izip(vr_inv_list, vpc_l3_list):
            test_stub.attach_all_l3_to_vpc_vr(vr_inv, l3_list)

    if flavor["has_vm"]:
        l3 = random.choice(vpc1_l3_list + vpc3_l3_list + vpc3_l3_list)
        vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(l3), l3_name=l3)
        test_obj_dict.add_vm(vm1)

    for vr_inv in vr_inv_list:
        vm_ops.destroy_vm(vr_inv.uuid)

    if flavor["has_vm"]:
        with test_lib.expected_failure('reboot vm in vpc l3 when no vpc vrouter', Exception):
            vm1.reboot()

def env_recover():
    test_stub.remove_all_vpc_vrouter()
    test_lib.lib_error_cleanup(test_obj_dict)






