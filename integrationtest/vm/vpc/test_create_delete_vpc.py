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
DefaultFalseDict = test_lib.DefaultFalseDict


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vpc_name_list = ['vpc1','vpc2','vpc3']
vpc_l3_list = [test_stub.vpc1_l3_list, test_stub.vpc2_l3_list, test_stub.vpc3_l3_list]
vr_list = []

case_flavor = dict(vr_only=             DefaultFalseDict(vr=True),
                   vr_attach_l3=        DefaultFalseDict(vr=True, attach_l3=True),
                   vr_attach_l3_has_vm= DefaultFalseDict(vr=True, attach_l3=True, has_vm=True)
                   )


@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")

    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))

    if flavor["attach_l3"]:
        for vr, l3_list in izip(vr_list, vpc_l3_list):
            test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    if flavor["has_vm"]:
        l3 = random.choice(test_stub.vpc1_l3_list + test_stub.vpc2_l3_list + test_stub.vpc2_l3_list)
        vm = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(l3), l3_name=l3)
        test_obj_dict.add_vm(vm)
        vm.check()

    for vr in vr_list:
        vr.destroy()

    if flavor["has_vm"]:
        with test_lib.expected_failure('reboot vm in vpc l3 when no vpc vrouter', Exception):
            vm.reboot()

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()






