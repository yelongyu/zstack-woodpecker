'''

New Integration Test for stop VM with qemu-guest-agent.

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

    out = test_lib.lib_execute_command_in_vm(vm.get_vm(), 'ps -ef |grep qemu-ga | grep -v grep')
    if not out.find('qemu-ga'):
        test_util.test_skip('qemu-ga not running on VM, skip testing')
    current_time = time.time()
    vm_ops.stop_vm(vm.get_vm().uuid)
    if time.time()-current_time >= 20:
        test_util.test_fail("VM should shutdown with default grace method in %s seconds" % (time.time()-current_time))
    vm.set_state(vm_header.STOPPED)
    vm.check()

    vm.start()
    vm.check()
    test_lib.lib_execute_command_in_vm(vm.get_vm(), 'nohup systemd-inhibit sleep 60 >/dev/null 2>/dev/null </dev/null &')
    current_time = time.time()
    vm_ops.stop_vm(vm.get_vm().uuid, force='cold')
    if time.time()-current_time >= 5:
        test_util.test_fail("VM should shutdown immediately with cold method, while it taks %s seconds" % (time.time()-current_time))

    vm.set_state(vm_header.STOPPED)
    vm.check()
  
    vm.destroy()
    test_util.test_pass('Stop VM with qemu-guest-agent Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
