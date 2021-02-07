'''

Simulator Test for affinity group antiHard policy.

@author: Chao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.affinitygroup_operations as ag_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import threading
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
exec_info = []
def create_vm(ag_uuid=None):
    global exec_info
    try:
        vm = test_stub.create_ag_vm(affinitygroup_uuid=ag_uuid)
        test_obj_dict.add_vm(vm)
    except:
        exec_info.append("failed")

def check_exception(expected):
    global exec_info
    if len(exec_info) != int(expected):
        test_util.test_fail("test failed")

def test():
    ag1 = ag_ops.create_affinity_group(name="ag1", policy="antiHard")
    for i in range(5):
        t = threading.Thread(target=create_vm, args=(ag1.uuid,))
        t.start()
    time.sleep(5)
    check_exception(2)
    vmuuids = []
    ag = test_lib.lib_get_affinity_group_by_name(name="ag1")
    for usage in ag.usages:
        vmuuids.append(usage.resourceUuid)
    test_util.test_logger("czhou %s" % vmuuids[0])
    assert len(vmuuids) == 3

    test_lib.lib_error_cleanup(test_obj_dict)
    ag_ops.delete_affinity_group(ag1.uuid)
    test_util.test_pass("Affinity Group antiHard policy pass")


#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

