'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.ipsec_operations as ipsec_ops
import zstackwoodpecker.test_state as test_state

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.create_ipsec_vpn_connection(check_connectivity=False)
    hybrid.del_vpn_connection(remote=False)
    test_util.test_pass('Sync Delete Vpc Vpn Connection Local Test Success')

def env_recover():
    if hybrid.vm:
        hyb_ops.destroy_vm_instance(hybrid.vm.vm.uuid)

    if hybrid.ipsec:
        ipsec_ops.delete_ipsec_connection(hybrid.ipsec.uuid)

    if hybrid.vpn_connection:
        hybrid.del_vpn_connection()

    if hybrid.user_vpn_gateway:
        hybrid.del_user_vpn_gateway()

    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    try:
        hybrid.del_vpn_connection()
    except:
        pass
    hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
