'''

New Integration Test for hybrid.

@author: Legion
'''

import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state


test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.add_datacenter_iz(region_id='cn-shanghai')
    hybrid.create_bucket(gc=True)
    time.sleep(5)
    hybrid.create_ecs_image(check_progress=True)
    test_util.test_pass('Get Create Ecs Image Progress Test Success')

def env_recover():
    try:
        hybrid.del_bucket()
    except:
        pass

    if hybrid.ecs_image:
        hybrid.del_ecs_image()

    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    hybrid.tear_down()
    try:
        hybrid.del_bucket()
    except:
        pass
    test_lib.lib_error_cleanup(test_obj_dict)
