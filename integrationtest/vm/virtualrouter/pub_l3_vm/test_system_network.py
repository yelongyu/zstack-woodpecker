'''

@author: FangSun

'''


import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import os
from zstackwoodpecker.operations import net_operations as net_ops
from zstackwoodpecker.operations import resource_operations as res_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


@test_lib.pre_execution_action(test_stub.remove_all_vr_vm)
def test():

    pub_l3_vm, flat_l3_vm, vr_l3_vm = test_stub.generate_pub_test_vm(tbj=test_obj_dict)

    with test_lib.expected_failure('create vm use system network', Exception):
        test_stub.create_vm_with_random_offering(vm_name='test_vm',
                                                 image_name='imageName_net',
                                                 l3_name='l3ManagementNetworkName')

    vr = test_lib.lib_find_vr_by_vm(vr_l3_vm.get_vm())[0]

    for nic in vr.vmNics:
        test_util.test_logger(nic.ip)
        if not test_lib.lib_check_directly_ping(nic.ip):
            test_util.test_fail('IP:{} expected to be able to ping vip while it fail'.format(nic.ip))


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)


