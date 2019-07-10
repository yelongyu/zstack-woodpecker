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
    hybrid.create_user_vpn_gateway()
#     hybrid.create_user_vpn_gateway(gc=True)

    hybrid.update_user_vpn_gateway(name='Vpc-User-Vpn-Gateway')
    hybrid.update_user_vpn_gateway(description='test-Vpc-User-Vpn-Gateway')

    time.sleep(60)
    hybrid.del_user_vpn_gateway()

    test_util.test_pass('Update Vpc User Vpn Gateway Remote Test Success')

def env_recover():
    if hybrid.user_vpn_gateway:
        time.sleep(60)
        try:
            hybrid.del_user_vpn_gateway()
        except:
            pass
    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
