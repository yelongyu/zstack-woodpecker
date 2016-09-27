'''
This case can not execute parallelly
@author: MengLai 
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.account_operations as account_operations

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    if res_ops.query_resource(res_ops.SFTP_BACKUP_STORAGE, conditions):
        sftp_backup_storage_uuid = res_ops.query_resource(res_ops.SFTP_BACKUP_STORAGE, conditions)[0].uuid
    else:
        test_util.test_skip("current test suite is for ceph, and there is no sftp. Skip test")

    recnt_timeout=5000
    test_util.test_dsc('Test SFTP Backup Storage Reconnect within %s ms' % recnt_timeout)
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm)

    zone_uuid = vm.get_vm().zoneUuid
    host = test_lib.lib_get_vm_host(vm.get_vm())
    host_uuid = host.uuid

    host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid, timeout=recnt_timeout) 
   
    vm.destroy()
    test_obj_dict.rm_vm(vm)

    test_util.test_pass('Reconnect Host within %s ms' % recnt_timeout)

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
