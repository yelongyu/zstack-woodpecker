'''

New stress test for create 1 vm with random configuration

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()



def test():
    vm = test_stub.create_random_vm()
    #vm.check()
    test_util.test_pass('Create 1 VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
