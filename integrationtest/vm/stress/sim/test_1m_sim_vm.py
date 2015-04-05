'''

New stress test for create 10m vm on 20k hosts.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import threading
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vm_goal = 2000000

def create_vm():
    vm = test_stub.create_random_vm()
    #test_obj_dict.add_vm(vm)
    vm.check()

def test():
    i = 0
    while i < vm_goal:
        thread = threading.Thread(target=create_vm, args=())
        wait_thread_queue()
        thread.start()
        i += 1

    test_util.test_pass('Create 1M VMs Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

def wait_thread_queue():
    while threading.active_count() > 1000:
        time.sleep(1)
