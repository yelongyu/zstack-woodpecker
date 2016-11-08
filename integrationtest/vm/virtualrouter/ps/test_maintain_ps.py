'''
New Integration Test for PS maintain mode.

@author: quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.host_operations as host_ops

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
ps_uuid = None
host_uuid = None

def test():
    global test_obj_dict
    global ps_uuid
    global host_uuid
    test_util.test_dsc('Create test vm and check')
    vm = test_stub.create_user_vlan_vm()
    host = test_lib.lib_get_vm_host(vm.get_vm())
    host_uuid = host.uuid
    test_obj_dict.add_vm(vm)
    vm.check()
    ps = lib_get_primary_storage_by_vm(vm)
    ps_uuid = ps.uuid
    ps_ops.change_primary_storage_state(ps_uuid, 'maintain')
    if not test_lib.lib_wait_target_down(vm.get_vm().vmNics[0].ip, '22', 90):
        test_util.test_fail('VM is expected to stop when PS change to maintain state')

    vm.set_state(vm_header.STOPPED)
    vm.check()
    ps_ops.change_primary_storage_state(ps_uuid, 'Enabled')
    host_ops.reconnect_host(host_uuid)

    vm.destroy()
    test_util.test_pass('PS maintain mode Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global ps_uuid
    if ps_uuid != None:
        ps_ops.change_primary_storage_state(ps_uuid, 'Enabled')
    global host_uuid
    if host_uuid != None:
        host_ops.reconnect_host(host_uuid)
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
