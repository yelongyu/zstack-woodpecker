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
    hybrid.add_datacenter_iz(check_vpn_gateway=True)
    hybrid.get_vpc(has_vpn_gateway=True)
    hybrid.create_route_entry(gc=True)
    time.sleep(90)
    hybrid.del_route_entry()
    test_util.test_pass('Create Delete Vpc Route Entry Test Success')

def env_recover():
    try:
        hybrid.del_route_entry()
    except:
        pass

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    try:
        hybrid.del_route_entry()
    except:
        pass
    test_lib.lib_error_cleanup(test_obj_dict)
