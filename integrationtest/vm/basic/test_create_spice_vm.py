'''

New Integration Test for creating KVM VM.

@author: ye.tian
'''

import zstackwoodpecker.test_util as test_util
import test_stub

vm = None

def test():
    global vm
    vm = test_stub.create_spice_vm()
    vm.check()
    test_stub.check_vm_spice(vm.vm.uuid)
    vm.destroy()
    vm.check()
    test_util.test_pass('Create VM with spice Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
