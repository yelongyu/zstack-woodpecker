'''

New Integration Test for creating KVM VM with ISO check VM reimage Capability.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import test_stub

vm = None
vm2 = None

def test():
    global vm
    vm = test_stub.create_vm_with_iso()
    vm.check()
    vm_capabilities = vm_ops.get_vm_capabilitys(vm.get_vm().uuid)
    if vm_capabilities.Capability.Reimage:
        test_util.test_pass('Create VM with ISO should not support reimage Test Success')
    vm.destroy()
    vm.check()

    vm2 = test_stub.create_vm()
    vm2.check()
    vm2_capabilities = vm_ops.get_vm_capabilitys(vm2.get_vm().uuid)
    if not vm2_capabilities.Capability.Reimage:
        test_util.test_pass('Create VM without ISO should support reimage Test Success')

    vm2.destroy()
    vm2.check()

    test_util.test_pass('Create VM with ISO Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global vm2
    if vm:
        try:
            vm.destroy()
        except:
            pass
    if vm2:
        vm2.destroy()
