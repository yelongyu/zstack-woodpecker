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
    hybrid.create_ecs_instance()
    test_obj_dict.add_hybrid_obj(hybrid)

    hybrid.update_ecs_instance(name='ECS-Instance')
    hybrid.update_ecs_instance(description='test-ECS-Instance')

    test_util.test_pass('Update ECS Instance Test Success')

def env_recover():
    time.sleep(120)
    try:
        hybrid.del_ecs_instance()
    except:
        pass
    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    if hybrid.ecs_instance:
        hybrid.del_ecs_instance()
    hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
