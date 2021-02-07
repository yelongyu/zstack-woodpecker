'''

Simulator Test for affinity group antiHard policy.

@author: Chao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.affinitygroup_operations as ag_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
def test():
    h1_name = os.environ.get("hostName")
    cond = res_ops.gen_query_conditions('name', '=', h1_name)
    h1 = res_ops.query_resource(res_ops.HOST, cond)
    ag1 = ag_ops.create_affinity_group(name="ag1", policy="antiHard")
    vm1 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid, host_uuid=h1[0].uuid)
    assert vm1.get_vm().hostUuid == h1[0].uuid
    test_obj_dict.add_vm(vm1)

    h2_name = os.environ.get("hostName2")
    cond = res_ops.gen_query_conditions('name', '=', h2_name)
    h2 = res_ops.query_resource(res_ops.HOST, cond)
    vm2 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid, host_uuid=h2[0].uuid)
    assert vm2.get_vm().hostUuid == h2[0].uuid
    test_obj_dict.add_vm(vm2)

    try:
        vm3 = None
        vm3 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid, host_uuid=h2[0].uuid)
    except:
        if not vm3:
            test_util.test_logger("vm3 isn't created as expected")
    finally:
        if vm3:
            test_util.test_fail("Test Fail, vm3 [uuid:%s] is not expected to be created" % vm3.get_vm().uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
    ag_ops.delete_affinity_group(ag1.uuid)
    test_util.test_pass("Affinity Group antiHard policy pass")
    

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
