'''

New Integration Test for creating KVM VM with ISO.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.image_operations as img_ops
import test_stub

vm = None
vm2 = None

def test():
    global vm
    global vm2
    vm = test_stub.create_vm_with_iso()
    vm.check()
    vm.destroy()
    vm.check()
    #create the vm with iso again, since there is a bug that 
    # vm creation with ISO failed with local storage.
    vm2 = test_stub.create_vm_with_previous_iso()
    vm2.check()
    vm2.destroy()

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
