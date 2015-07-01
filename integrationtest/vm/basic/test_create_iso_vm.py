'''

New Integration Test for creating KVM VM with ISO.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.image_operations as img_ops
import test_stub

vm = None

def test():
    global vm
    vm = test_stub.create_vm_with_iso()
    vm.check()
    vm.destroy()
    vm.check()

    test_util.test_pass('Create VM with ISO Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
