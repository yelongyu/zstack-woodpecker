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
#     hybrid.add_datacenter_iz()
    hybrid.add_datacenter_iz(check_prepaid_ecs=True, ks2=True)
    hybrid.create_aliyun_disk()
    time.sleep(90)
    hybrid.del_aliyun_disk()
    test_util.test_pass('Create Aliyun Disk Test Success')

def env_recover():
    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
