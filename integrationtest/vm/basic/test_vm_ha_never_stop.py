'''

New Integration Test for VM ha never stop operation

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import time

vm = None

def test():
    global vm
    vm = test_stub.create_vm()
    vm.check()
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    vm.stop()
    time.sleep(60)
    vm.set_state(test_vm_header.RUNNING)
    vm.check()
    vm.destroy()
    vm.check()
    test_util.test_pass('VM ha never stop Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
