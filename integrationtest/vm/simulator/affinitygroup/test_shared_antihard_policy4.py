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
    ag1 = ag_ops.create_affinity_group(name="ag1", policy="antiHard")
    vm1 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    test_obj_dict.add_vm(vm1)

    vm2 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    test_obj_dict.add_vm(vm2)
    assert vm1.get_vm().hostUuid != vm2.get_vm().hostUuid
  
    vm3 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    test_obj_dict.add_vm(vm3)
    assert vm1.get_vm().hostUuid != vm3.get_vm().hostUuid
    assert vm2.get_vm().hostUuid != vm3.get_vm().hostUuid

    try:
        vm4 = None
        vm4 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    except:
        if not vm4:
            test_util.test_logger("vm4 isn't created as expected")
    finally:
        if vm4:
            test_util.test_fail("Test Fail, vm4 [uuid:%s] is not expected to be created" % vm4.get_vm().uuid)
    vm1.destroy()
    vm1.expunge()
    vm4 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    test_obj_dict.add_vm(vm4)
    assert vm4.get_vm().hostUuid != vm2.get_vm().hostUuid
    assert vm4.get_vm().hostUuid != vm3.get_vm().hostUuid
    vmuuids = []
    #vm2.stop()
    ag = test_lib.lib_get_affinity_group_by_name(name="ag1")
    for usage in ag.usages:
        vmuuids.append(usage.resourceUuid)
    assert vm2.get_vm().uuid in vmuuids       

    try:
        vm5 = None
        vm5 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    except:
        if not vm5:
            test_util.test_logger("vm5 isn't created as expected")
    finally:
        if vm5:
            test_util.test_fail("Test Fail, vm5 [uuid:%s] is not expected to be created" % vm5.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
    ag_ops.delete_affinity_group(ag1.uuid)
    test_util.test_pass("Affinity Group antiHard policy pass")
    

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
