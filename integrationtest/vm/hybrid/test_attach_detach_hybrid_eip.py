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
    test_obj_dict.add_hybrid_obj(hybrid)
    hybrid.get_eip()
    hybrid.attach_eip_to_ecs()
    hybrid.detach_eip_from_ecs()
    hybrid.del_ecs_instance()
    try:
        hybrid.del_eip()
    except:
        pass
    test_util.test_pass('Attach Detach Hybrid Eip to/from Ecs Test Success')

def env_recover():
    try:
        hybrid.del_eip()
    except:
        pass
    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        hybrid.del_eip()
    except:
        pass
