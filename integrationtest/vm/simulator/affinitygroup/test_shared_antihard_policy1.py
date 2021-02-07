'''

Simulator Test for affinity group antiHard policy.

@author: Chao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.affinitygroup_operations as ag_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
def test():
    ag1 = ag_ops.create_affinity_group(name="ag1", policy="antiHard")
    vm1 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_ag_vm(host_uuid=vm1.get_vm().hostUuid)
    test_obj_dict.add_vm(vm2)
    assert vm2.get_vm().hostUuid == vm1.get_vm().hostUuid
    vm2.stop()
    ag_ops.add_vm_to_affinity_group(ag1.uuid, vm2.get_vm().uuid)
    vm2.start()
    assert vm2.get_vm().hostUuid != vm1.get_vm().hostUuid
    test_lib.lib_error_cleanup(test_obj_dict)
    ag_ops.delete_affinity_group(ag1.uuid)
    test_util.test_pass("Affinity Group antiHard policy pass")
    

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
