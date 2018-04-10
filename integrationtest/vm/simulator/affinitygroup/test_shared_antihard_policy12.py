'''

Simulator Test for affinity group antiHard policy.

@author: Chao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.affinitygroup_operations as ag_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
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
    test_obj_dict.add_vm(vm1)

    vm1.stop()
    
    hosts = vm_ops.get_vm_starting_candidate(vm1.get_vm().uuid, systemtag=["affinityGroupUuid::%s" % ag1.uuid])
    assert len(hosts) == 3
    test_lib.lib_error_cleanup(test_obj_dict)
    ag_ops.delete_affinity_group(ag1.uuid)
    test_util.test_pass("Affinity Group antiHard policy pass")
    

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
