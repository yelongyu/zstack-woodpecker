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
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.account_operations as account_operations
import zstacklib.utils.ssh as ssh
import socket

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global sftp_backup_storage_uuid
    global sftp_backup_storage_hostname
    global recnt_timeout
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    if res_ops.query_resource(res_ops.SFTP_BACKUP_STORAGE, conditions):
        sftp_backup_storage_uuid = res_ops.query_resource(res_ops.SFTP_BACKUP_STORAGE, conditions)[0].uuid
        sftp_backup_storage_hostname = res_ops.query_resource(res_ops.SFTP_BACKUP_STORAGE, conditions)[0].hostname
    else:
        test_util.test_skip("current test suite is for ceph, and there is no sftp. Skip test")

    local_ip = socket.gethostbyname(socket.gethostname())
    sftp_hostname = res_ops.query_resource(res_ops.SFTP_BACKUP_STORAGE, conditions)[0].hostname
    test_util.test_dsc("local ip:%s, sftp ip:%s" % (local_ip, sftp_hostname))
    if local_ip != sftp_hostname:
        test_util.test_skip("host of sftp and host of MN are not the same one. Skip test") 

    test_util.test_dsc('Test SFTP Backup Storage Update Infomation: hostname')

    test_util.test_dsc('Update Hostname')
    test_util.test_dsc('Create New VM as Sftp')
    vm = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm)

    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
  
    vm.check()
    test_lib.lib_execute_command_in_vm(vm.get_vm(), 'mkdir /home/sftpBackupStorage')

    bs_ops.update_sftp_backup_storage_info(sftp_backup_storage_uuid, 'hostname', vm_ip)
    host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid)

    test_util.test_dsc('Recover Sftp Hostname')
    bs_ops.update_sftp_backup_storage_info(sftp_backup_storage_uuid, 'hostname', sftp_backup_storage_hostname)
    host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid)

    vm.destroy()
    test_obj_dict.rm_vm(vm)

    test_util.test_pass('SFTP Backup Storage Update Infomation SUCCESS')

#Will be called only if exception happens in test().
def error_cleanup():
    global sftp_backup_storage_uuid
    global sftp_backup_storage_hostname
    global recnt_timeout
    bs_ops.update_sftp_backup_storage_info(sftp_backup_storage_uuid, 'hostname', sftp_backup_storage_hostname)
    host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
