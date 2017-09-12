'''

New Integration Test for hybrid.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops


test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.add_datacenter_iz()
    hybrid.get_vpc()
    hybrid.get_vswitch()
    hybrid.get_sg()
    hybrid.get_sg_rule()
    cond_sg_rule = res_ops.gen_query_conditions('ecsSecurityGroupUuid', '=', hybrid.sg.uuid)
    assert hyb_ops.query_ecs_security_group_rule_local(cond_sg_rule)
    test_util.test_pass('Sync Delete Ecs Security Group Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
