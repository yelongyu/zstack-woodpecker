'''

New Integration Test for VM ha never stop with delete and recover

@author: quarkonics
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
    vm.destroy()
    vm.recover()
    time.sleep(60)
    vm.set_state(vm_header.RUNNING)
    vm.check()
    vm.destroy()
    test_util.test_pass('VM ha never stop with delete and recover Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
