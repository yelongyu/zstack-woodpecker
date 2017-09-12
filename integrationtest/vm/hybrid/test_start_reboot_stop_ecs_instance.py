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
    hybrid.create_ecs_instance()
    hybrid.reboot_ecs()
    hybrid.stop_ecs()
    hybrid.start_ecs()
    test_util.test_pass('Start Reboot Stop Ecs Instance Test Success')

def env_recover():
    if hybrid.ecs_instance:
        hybrid.del_ecs_instance()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
