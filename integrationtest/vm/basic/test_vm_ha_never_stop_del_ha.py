'''

New Integration Test for VM could stop after delete ha never stop

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import time

test_stub = test_lib.lib_get_specific_stub()

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
    ha_ops.del_vm_instance_ha_level(vm.get_vm().uuid)
    vm.stop()
    vm.check()
    vm.destroy()
    vm.check()
    test_util.test_pass('VM delete ha never stop Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()

