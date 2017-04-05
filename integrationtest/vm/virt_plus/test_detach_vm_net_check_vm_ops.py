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

def test():
    delete_policy = test_lib.lib_set_delete_policy('vm', 'Delay')
    vm = test_stub.create_vm(vm_name = 'basic-test-vm')
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_nic_uuid = vm.vm.vmNics[0].uuid
    net_ops.detach_l3(vm_nic_uuid)

    vm.destroy()
    vm.check()

    vm.resume()
    vm.check()

    vm.start()
    vm.check()

    test_lib.lib_set_delete_policy('vm', delete_policy)
    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
