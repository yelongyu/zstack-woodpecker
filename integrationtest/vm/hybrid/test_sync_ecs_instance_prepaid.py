'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.add_datacenter_iz(check_prepaid_ecs=True, ks2=True)
    if hybrid.prepaid_ecs:
        test_util.test_pass('Sync Prepaid ECS Instance Test Success')
    else:
        test_util.test_fail('Sync Prepaid ECS Instance Test Fail')


#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
