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
    hybrid.add_datacenter_iz(add_datacenter_only=True)
    hybrid.create_eip()
    time.sleep(10)

    hybrid.update_eip(name='Hybrid-EIP')
    hybrid.update_eip(description='test-Hybrid-EIP')

    test_util.test_pass('Update Hybrid Eip Test Success')

def env_recover():
    if hybrid.eip:
        hybrid.del_eip()
    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
