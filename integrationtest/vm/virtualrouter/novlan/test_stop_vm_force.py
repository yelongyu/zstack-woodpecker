'''

New Integration Test for force stop VM.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.header.vm as vm_header
import time
import os
import tempfile
import uuid
import threading

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def prevent_vm_stop(vm):
    test_lib.lib_execute_command_in_vm(vm, 'systemd-inhibit sleep 60')

def test():
    vm = test_stub.create_user_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm.check()
    thread = threading.Thread(target = prevent_vm_stop)
    thread.daemon = True
    thread.start()

    current_time = time.time()
    vm_ops.stop_vm(vm.get_vm().uuid)
    if time.time()-current_time <= 10:
        test_util.test_fail("VM should not shutdown with default grace method in %s seconds" % (time.time()-current_time))
    while threading.active_count() >= 1:
        time.sleep(1)
    vm.set_state(vm_header.STOPPED)
    vm.check()

    vm.start()
    vm.check()
    thread = threading.Thread(target = prevent_vm_stop)
    thread.daemon = True
    thread.start()

    current_time = time.time()
    vm_ops.stop_vm(vm.get_vm().uuid, force='cold')
    if time.time()-current_time >= 5:
        test_util.test_fail("VM should shutdown immediately with cold method, while it taks %s seconds" % (time.time()-current_time))
    while threading.active_count() >= 1:
        time.sleep(1)
    vm.set_state(vm_header.STOPPED)
    vm.check()
  
    vm.destroy()
    test_util.test_pass('Force Stop VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
