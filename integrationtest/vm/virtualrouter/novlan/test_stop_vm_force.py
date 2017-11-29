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

def test():
    vm = test_stub.create_user_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm.check()

    vrs = test_lib.lib_find_flat_dhcp_vr_by_vm(vm.vm)
    if len(vrs) == 1:        
        cold_threshold = 10
    else:
        cold_threshold = 5

    test_lib.lib_execute_command_in_vm(vm.get_vm(), 'systemctl stop qemu-guest-agent')
    test_lib.lib_execute_command_in_vm(vm.get_vm(), 'nohup systemd-inhibit sleep 60 >/dev/null 2>/dev/null </dev/null &')
    current_time = time.time()
    vm_ops.stop_vm(vm.get_vm().uuid)
    if time.time()-current_time <= 10:
        test_util.test_fail("VM should not shutdown with default grace method in %s seconds" % (time.time()-current_time))
    vm.set_state(vm_header.STOPPED)
    vm.check()

    vm.start()
    vm.check()
    test_lib.lib_execute_command_in_vm(vm.get_vm(), 'nohup systemd-inhibit sleep 60 >/dev/null 2>/dev/null </dev/null &')
    current_time = time.time()
    vm_ops.stop_vm(vm.get_vm().uuid, force='cold')
    if time.time()-current_time >= cold_threshold:
        test_util.test_fail("VM should shutdown immediately with cold method, while it taks %s seconds" % (time.time()-current_time))

    vm.set_state(vm_header.STOPPED)
    vm.check()
  
    vm.destroy()
    test_util.test_pass('Force Stop VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
