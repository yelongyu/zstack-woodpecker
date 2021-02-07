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
    hybrid.create_aliyun_disk()
    hybrid.attach_aliyun_disk()
    time.sleep(90)
    hybrid.detach_aliyun_disk()
    time.sleep(60)
    hybrid.del_aliyun_disk()
    test_util.test_pass('Attach Aliyun Disk Test Success')

def env_recover():
    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
