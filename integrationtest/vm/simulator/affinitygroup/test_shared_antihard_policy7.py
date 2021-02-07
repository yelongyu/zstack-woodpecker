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

    vm2.stop()
  
    vm4 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    test_obj_dict.add_vm(vm4)
    assert vm2.get_vm().hostUuid != vm1.get_vm().hostUuid
    assert vm2.get_vm().hostUuid != vm3.get_vm().hostUuid

    try:
        vm2.start()
    except:
        test_util.test_logger("vm2 isn't started as expected")
    finally:
        if vm2.state == 'Running':
            test_util.test_fail("Test Fail, vm2 [uuid:%s] is not expected to be started" % vm2.get_vm().uuid)
    ag = test_lib.lib_get_affinity_group_by_name(name="ag1")

    test_lib.lib_error_cleanup(test_obj_dict)
    ag_ops.delete_affinity_group(ag1.uuid)
    test_util.test_pass("Affinity Group antiHard policy pass")
    

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
