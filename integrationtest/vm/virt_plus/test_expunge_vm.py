'''

New Integration Test for expunging KVM VM.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

_config_ = {
        'timeout' : 100,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
delete_policy = test_lib.lib_set_delete_policy('vm', 'Delay')

def test():
    vm = test_stub.create_vm(vm_name = 'basic-test-vm')
    test_obj_dict.add_vm(vm)
    time.sleep(1)
    vm.destroy()
    vm.expunge()
    test_lib.lib_set_delete_policy('vm', delete_policy)
    test_util.test_pass('Expunge VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_lib.lib_set_delete_policy('vm', delete_policy)
