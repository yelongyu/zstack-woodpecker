'''

New Integration Test for detach ISO on running VM.

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
    img_ops.detach_iso(vm.get_vm().uuid)
    vm.destroy()
    vm.check()

    test_util.test_pass('Create detach VM ISO Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
