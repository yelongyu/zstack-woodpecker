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
    hybrid.add_datacenter_iz(add_datacenter_only=True)
    hybrid.get_eip()
    hybrid.del_eip(remote=False)
    test_util.test_pass('Sync Delete Hybrid Eip Test Success')

def env_recover():
    if hybrid.eip_create:
        hybrid.get_eip(sync_eip=True)
        hybrid.del_eip()
    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    hybrid.tear_down()
    try:
        hybrid.get_eip(sync_eip=True)
        hybrid.del_eip()
    except:
        pass
    test_lib.lib_error_cleanup(test_obj_dict)
