'''

New Integration Test for hybrid.

@author: Quarkonics
'''

import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.add_datacenter_iz(add_datacenter_only=True)
    hybrid.add_bucket()
    hybrid.create_ecs_image()
    time.sleep(300)
    hybrid.del_ecs_image()
    test_util.test_pass('Create Delete Ecs Image Test Success')

def env_recover():
    if hybrid.ecs_image:
        time.sleep(60)
        try:
            hybrid.del_ecs_image()
        except:
            pass

    if hybrid.oss_bucket_create:
        hybrid.del_bucket()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
