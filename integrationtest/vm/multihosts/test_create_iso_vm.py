'''

New Integration Test for creating KVM VM with ISO.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.image_operations as img_ops
import os

test_stub = test_lib.lib_get_specific_stub()

vm = None
vm2 = None

def test():
    global vm
    global vm2
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm = test_stub.create_vm_with_fake_iso('fake_iso_vm', l3_name)

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

