'''

New Integration Test for VM shutdown with ha mode OnHostFailure

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import time

vm = None

def test():
    global vm
    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    vm = test_stub.create_vm()
    vm.check()
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "OnHostFailure")
    rsp = test_lib.lib_execute_ssh_cmd(vm.get_vm().vmNics[0].ip, test_lib.lib_get_vm_username(vm.get_vm()), test_lib.lib_get_vm_password(vm.get_vm()), 'init 0')
    time.sleep(60)
    vm.check()
    vm.destroy()
    vm.check()
    test_util.test_pass('VM shutdown with ha mode OnHostFailure Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
