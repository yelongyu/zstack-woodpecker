'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.ipsec_operations as ipsec_ops
import time

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.create_ipsec_vpn_connection()

def env_recover():
    if hybrid.vm:
        hyb_ops.destroy_vm_instance(hybrid.vm.vm.uuid)

    if hybrid.ecs_instance:
        hybrid.del_ecs_instance()

    if hybrid.ipsec:
        ipsec_ops.delete_ipsec_connection(hybrid.ipsec.uuid)

    if hybrid.vpn_connection:
        hybrid.del_vpn_connection()

    if hybrid.user_vpn_gateway:
        hybrid.del_user_vpn_gateway()

    if hybrid.sg_create:
        time.sleep(30)
        hybrid.del_sg()

    if hybrid.eip:
        try:
            hybrid.del_eip()
        except:
            pass

    if hybrid.route_entry:
        hybrid.del_route_entry()

    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
