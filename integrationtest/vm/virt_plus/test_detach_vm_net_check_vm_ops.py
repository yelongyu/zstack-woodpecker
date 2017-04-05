'''
New Integration Test for detaching vm network and check vm ops.
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
delete_policy = None

def test():
    global test_obj_dict
    global delete_policy
    delete_policy = test_lib.lib_set_delete_policy('vm', 'Delay')
    vm = test_stub.create_vm(vm_name = 'basic-test-vm')
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_nic_uuid = vm.vm.vmNics[0].uuid
    net_ops.detach_l3(vm_nic_uuid)

    vm.destroy()
    vm.check()

    vm.recover()
    vm.check()

    test_lib.lib_set_delete_policy('vm', delete_policy)
    try:
        vm.start()
    except Exception, e:
        if "please attach a nic and try again" in str(e):
            test_util.test_pass('test detach l3 check vm passed.')

    test_util.test_fail('test detach l3 check vm status is not as expected, expected should be not started with error message have not nic.')


def env_recover():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)



#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    global delete_policy
    test_lib.lib_error_cleanup(test_obj_dict)
    test_lib.lib_set_delete_policy('vm', delete_policy)
