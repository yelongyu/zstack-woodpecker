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
    hybrid.create_vpc()
    time.sleep(90)
    hybrid.del_vpc()
    test_util.test_pass('Create Delete ECS VPC Test Success')

def env_recover():
    try:
        hybrid.del_vpc()
    except:
        pass

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    try:
        hybrid.del_vpc()
    except:
        pass
    test_lib.lib_error_cleanup(test_obj_dict)
