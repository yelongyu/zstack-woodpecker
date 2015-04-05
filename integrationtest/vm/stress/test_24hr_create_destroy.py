'''

For stress Testing: keep creating/destroying vm in 24hr

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

duration = 24*60*60

def test():
    current_time = time.time()
    end_time = current_time + duration
    while current_time < end_time:
        times = times + 1
        vm = test_stub.create_vlan_vm()
        #vm = test_stub.create_vlan_vm_with_volume()
        time.sleep(5)
        #need clean up log files in virtual router when doing stress test
        if times % 100 == 99:
            test_lib.lib_check_cleanup_vr_logs_by_vm(vm.vm)

        vm.destroy()
    test_util.test_pass('Keep create/destroy %s VMs in 24 hrs pass' % times)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
