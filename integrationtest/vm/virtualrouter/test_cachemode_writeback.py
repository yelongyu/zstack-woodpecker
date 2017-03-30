'''

New Integration Test for cackemode change.

@author: Glody 
'''

import os

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.config_operations as conf_ops

_config_ = {
        'timeout' : 600,
        'noparallel' : True
        }
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
   
    target_value = "writeback" 

    global test_obj_dict
    vm = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm)
    vm.check()

    pre_value = conf_ops.change_global_config("kvm", "vm.cacheMode", target_value)
    vm_cacheMode = conf_ops.get_global_config_value("kvm", "vm.cacheMode")
    if vm_cacheMode != target_value:
        test_util.test_fail('change value of vm.cacheMode failed. target value is %s, real value is %s' %(target_value, vm_cacheMode))

    #set back to defualt
    conf_ops.change_global_config("kvm", "vm.cacheMode", pre_value)
    vm_cacheMode = conf_ops.get_global_config_value("kvm", "vm.cacheMode")

    if vm_cacheMode != pre_value:
        test_util.test_fail('Reset vm.cacheMode Value to Default Fail.')

    vm.destroy()
    test_util.test_pass('vm.cacheMode Change Pass.')
    

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict) 
