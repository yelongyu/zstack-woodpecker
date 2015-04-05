'''

For Stress Testing: create 1 VM without VR and destroy it after 3s. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import time
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

parallel_num = 10

def test():
    vm = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm)
 
    time.sleep(3)
    vm.destroy()
    test_util.test_pass('Create/Destroy VM with VR successfully')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
