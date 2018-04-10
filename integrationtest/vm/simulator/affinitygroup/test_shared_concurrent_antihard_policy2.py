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
    vm1 = test_stub.create_ag_vm(host_uuid=h1[0].uuid)
    assert vm1.get_vm().hostUuid == h1[0].uuid
    test_obj_dict.add_vm(vm1)

    new_vm = vm1.clone(names=["clone-vm1", "clone-vm2", "clone-vm3"], systemtag=["affinityGroupUuid::%s" % ag1.uuid])
    test_obj_dict.add_vm(new_vm[0])
    test_obj_dict.add_vm(new_vm[1])
    test_obj_dict.add_vm(new_vm[2])
    vmuuids = []
    ag = test_lib.lib_get_affinity_group_by_name(name="ag1")
    for usage in ag.usages:
        vmuuids.append(usage.resourceUuid)
    assert new_vm[0].get_vm().uuid in vmuuids
    assert new_vm[1].get_vm().uuid in vmuuids
    assert new_vm[2].get_vm().uuid in vmuuids
    assert len(vmuuids) == 3
    
    try:
        ag_ops.add_vm_to_affinity_group(ag1.uuid, vm1.get_vm().uuid) 
    except:
        test_util.test_logger("vm1 is not expected to add into affinity group [uuid: %s]" % ag1.uuid)
    vmuuids = []
    ag = test_lib.lib_get_affinity_group_by_name(name="ag1")
    for usage in ag.usages:
        vmuuids.append(usage.resourceUuid)
    assert vm1.get_vm().uuid not in vmuuids
 
    test_lib.lib_error_cleanup(test_obj_dict)
    ag_ops.delete_affinity_group(ag1.uuid)
    test_util.test_pass("Affinity Group antiHard policy pass")
    

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
