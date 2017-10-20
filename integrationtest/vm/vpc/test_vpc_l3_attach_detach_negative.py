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


all_vpc_l3_list = ['l3VlanNetworkName1'] + ["l3VlanNetwork{}".format(i) for i in xrange(2,11)] + \
                  ["l3VxlanNetwork{}".format(i) for i in xrange(11,21)]


@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
def test():

    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")

    vr_inv1 = test_stub.create_vpc_vrouter("vpc1")
    vr_inv2 = test_stub.create_vpc_vrouter("vpc2")

    test_util.test_dsc("create vm in ")

    test_stub.attach_all_l3_to_vpc_vr(vr_inv1, ['l3VlanNetworkName1'])
    with test_lib.expected_failure('Attach vpc l3 to vpc2 which is already attached to vpc1', Exception):
        test_stub.attach_all_l3_to_vpc_vr(vr_inv2, ['l3VlanNetworkName1'])

    vm = test_stub.create_vm_with_random_offering(vm_name='vpc_vm', l3_name='l3VlanNetworkName1')
    test_obj_dict.add_vm(vm)
    vm.check()

    test_util.test_dsc("Try to create vm in l3: l3VlanNetworkName1")
    with test_lib.expected_failure('Detach vpc l3 when have vm running on it', Exception):
        nic_uuid_list = [nic.uuid for nic in vr_inv1.vmNics if nic.metaData == '4']
        for nic_uuid in nic_uuid_list:
            net_ops.detach_l3(nic_uuid)

    test_util.test_dsc("Destroy vm and detach it again")
    vm.destroy()
    nic_uuid_list = [nic.uuid for nic in vr_inv1.vmNics if nic.metaData == '4']
    for nic_uuid in nic_uuid_list:
        net_ops.detach_l3(nic_uuid)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

