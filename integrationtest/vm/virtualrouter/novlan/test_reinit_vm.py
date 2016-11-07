'''

New Integration Test for reinit VM.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    vm = test_stub.create_user_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm.check()
    vm.stop()
    vm.reinit()
    vm.update()
    vm.check()
    vm.destroy()
    test_util.test_pass('Re-init VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
