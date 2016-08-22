'''

New Integration Test for cloning KVM VM 2 times.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vn_prefix = 'vm-clone-%s' % time.time()
vm_name1 = ['%s-vm1']
vm_name2 = ['%s-vm2']

def test():
    vm = test_stub.create_vm(vm_name = vn_prefix)
    test_obj_dict.add_vm(vm)
    new_vm1 = vm.clone(vm_name1)[0]
    test_obj_dict.add_vm(new_vm1)
    vm.destroy()
    test_obj_dict.rm_vm(vm)

    new_vm2 = new_vm1.clone(vm_name2)[0]
    test_obj_dict.add_vm(new_vm2)

    new_vm2.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Clone VM Test 2 Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
