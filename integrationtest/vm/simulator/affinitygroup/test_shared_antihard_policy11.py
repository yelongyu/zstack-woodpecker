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
    ag_ops.add_vm_to_affinity_group(ag1.uuid, vm1.get_vm().uuid)
    test_obj_dict.add_vm(vm1)

    h2_name = os.environ.get("hostName2")
    cond = res_ops.gen_query_conditions('name', '=', h2_name)
    h2 = res_ops.query_resource(res_ops.HOST, cond)
    vm2 = test_stub.create_ag_vm(host_uuid=h2[0].uuid)
    assert vm2.get_vm().hostUuid == h2[0].uuid
    ag_ops.add_vm_to_affinity_group(ag1.uuid, vm2.get_vm().uuid)
    test_obj_dict.add_vm(vm2)

    h3_name = os.environ.get("hostName3")
    cond = res_ops.gen_query_conditions('name', '=', h3_name)
    h3 = res_ops.query_resource(res_ops.HOST, cond)
    vm3 = test_stub.create_ag_vm(host_uuid=h3[0].uuid)
    assert vm3.get_vm().hostUuid == h3[0].uuid
    ag_ops.add_vm_to_affinity_group(ag1.uuid, vm3.get_vm().uuid)
    test_obj_dict.add_vm(vm3)

    vm4 = test_stub.create_ag_vm(host_uuid=h1[0].uuid)
    test_obj_dict.add_vm(vm4)

    try:
        ag_ops.add_vm_to_affinity_group(ag1.uuid, vm4.get_vm().uuid) 
    except:
        test_util.test_logger("vm4 is not expected to add into affinity group [uuid: %s]" % ag1.uuid)
    vmuuids = []
    ag = test_lib.lib_get_affinity_group_by_name(name="ag1")
    for usage in ag.usages:
        vmuuids.append(usage.resourceUuid)
    assert vm4.get_vm().uuid not in vmuuids
 
    ag_ops.remove_vm_from_affinity_group(affinityGroupUuid=ag1.uuid, vm_uuid=vm1.get_vm().uuid)
    ag_ops.add_vm_to_affinity_group(ag1.uuid, vm4.get_vm().uuid)
    vmuuids = []
    ag = test_lib.lib_get_affinity_group_by_name(name="ag1")
    for usage in ag.usages:
        vmuuids.append(usage.resourceUuid)
    assert vm4.get_vm().uuid in vmuuids

    test_lib.lib_error_cleanup(test_obj_dict)
    ag_ops.delete_affinity_group(ag1.uuid)
    test_util.test_pass("Affinity Group antiHard policy pass")
    

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
