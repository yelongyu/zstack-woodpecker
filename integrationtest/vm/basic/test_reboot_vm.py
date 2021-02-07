'''

New Integration Test for rebooting VM operation

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_specific_stub()

vm = None

def test():
    global vm
    vm = test_stub.create_vm()
    vm.check()
    vm.reboot()
    vm.check()
    vm.destroy()
    vm.check()
    test_util.test_pass('Reboot VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()

