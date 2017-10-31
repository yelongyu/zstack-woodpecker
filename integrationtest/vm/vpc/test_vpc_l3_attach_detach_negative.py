'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import time
import random
import os
from itertools import izip


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
def test():

    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")

    vr1 = test_stub.create_vpc_vrouter("vpc1")
    vr2 = test_stub.create_vpc_vrouter("vpc2")

    test_util.test_dsc("create vm in ")

    test_stub.attach_l3_to_vpc_vr(vr1, ['l3VlanNetworkName1'])
    with test_lib.expected_failure('Attach vpc l3 to vpc2 which is already attached to vpc1', Exception):
        test_stub.attach_l3_to_vpc_vr(vr2, ['l3VlanNetworkName1'])

    test_util.test_dsc("Try to create vm in l3: l3VlanNetworkName1")
    vm = test_stub.create_vm_with_random_offering(vm_name='vpc_vm', l3_name='l3VlanNetworkName1')
    test_obj_dict.add_vm(vm)
    vm.check()

    with test_lib.expected_failure('Detach vpc l3 when have vm running on it', Exception):
        nic_uuid_list = [nic.uuid for nic in vr1.inv.vmNics if nic.metaData == '4']
        for nic_uuid in nic_uuid_list:
            vr1.remove_nic(nic_uuid)

    test_util.test_dsc("Destroy vm and detach it again")
    vm.destroy()
    nic_uuid_list = [nic.uuid for nic in vr1.inv.vmNics if nic.metaData == '4']
    for nic_uuid in nic_uuid_list:
        vr1.remove_nic(nic_uuid)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

