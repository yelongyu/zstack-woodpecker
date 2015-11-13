'''

New Integration test for testing vm migration between hosts.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()

def test():
    if test_lib.lib_get_active_host_number() < 2:
        test_util.test_skip('There is not 2 or more hosts to do migration test')

    vm = test_stub.create_vm(vm_name = 'test-vm-migration')
    test_obj_dict.add_vm(vm)
    vm.check()
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    vm.destroy()
    test_util.test_pass('Migrate VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

