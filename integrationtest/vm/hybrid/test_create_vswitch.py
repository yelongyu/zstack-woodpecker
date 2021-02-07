'''

New Integration Test for hybrid.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import time


test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.add_datacenter_iz()
    hybrid.get_vpc()
    hybrid.create_vswitch()
    time.sleep(30)
    hybrid.del_vswitch()
    test_util.test_pass('Create ECS VSwitch Test Success')

def env_recover():
    try:
        hybrid.del_vswitch()
    except:
        pass

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    try:
        hybrid.del_vswitch()
    except:
        pass
    test_lib.lib_error_cleanup(test_obj_dict)
