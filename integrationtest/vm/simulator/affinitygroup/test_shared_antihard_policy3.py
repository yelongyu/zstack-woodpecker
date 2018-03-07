'''

Simulator Test for affinity group antiHard policy.

@author: Chao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.affinitygroup_operations as ag_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import test_stub
import os

test_obj_dict = test_state.TestStateDict()
def test():
    ag1 = ag_ops.create_affinity_group(name="ag1", policy="antiHard")
    vm1 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    test_obj_dict.add_vm(vm1)

    vm2 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    test_obj_dict.add_vm(vm2)
    assert vm1.hostUuid != vm2.hostUuid
  
    vm3 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    test_obj_dict.add_vm(vm3)
    assert vm1.hostUuid != vm3.hostUuid
    assert vm2.hostUuid != vm3.hostUuid

    try:
        vm4 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    except:
        test_util.test_logger("vm4 [uuid:%s] isn't created as expected" % vm4.uuid)
    finally:
        if vm4:
            test_util.test_fail("Test Fail, vm4 [uuid:%s] is not expected to be created" % vm4.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass("Affinity Group antiHard policy pass")
    

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
