'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import time


test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.create_ecs_instance(allocate_eip=True, connect=True)
    test_obj_dict.add_hybrid_obj(hybrid)
#     hybrid.get_eip(in_use=True)
    hybrid.check_eip_accessibility(hybrid.ecs_instance.publicIpAddress)
    time.sleep(300)
    hybrid.del_ecs_instance()
    test_util.test_pass('Create Ecs Instance with Public IP Test Success')

def env_recover():
    hybrid.tear_down()


#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
