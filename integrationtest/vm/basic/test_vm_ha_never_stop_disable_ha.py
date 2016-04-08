'''

New Integration Test for VM could stop after disable ha

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
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    vm.stop()
    time.sleep(60)
    vm.set_state(vm_header.RUNNING)
    vm.check()
    test_lib.lib_set_ha_enable('false')
    vm.stop()
    vm.check()
    vm.destroy()
    vm.check()
    test_lib.lib_set_ha_enable('true')
    test_util.test_pass('VM stop with disable ha Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    test_lib.lib_set_ha_enable('true')
    if vm:
        vm.destroy()
