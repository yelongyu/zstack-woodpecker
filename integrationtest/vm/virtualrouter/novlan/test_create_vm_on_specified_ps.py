'''

@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    test_util.test_dsc('Create test vm on each ps and check')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    pss = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond)

    ps_list_for_vm_creation = pss[:]
    if test_stub.find_ps_local() and test_stub.find_ps_nfs():
        ps_list_for_vm_creation = [ps for ps in pss if ps.type != inventory.NFS_PRIMARY_STORAGE_TYPE]

    for ps in ps_list_for_vm_creation:
        vm = test_stub.create_specified_ps_vm(ps_uuid = ps.uuid)
        test_obj_dict.add_vm(vm)
        vm.check()
        if test_lib.lib_get_primary_storage_by_vm(vm.get_vm()).uuid != ps.uuid:
            test_util.test_pass('[vm:] %s is expected to create on [ps:] %s' % (vm.get_vm().uuid, ps.uuid))
        vm.destroy()

    test_util.test_pass('Create VirtualRouter VM on each PS Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
