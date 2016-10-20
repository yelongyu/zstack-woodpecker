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

    recnt_timeout=5000
    test_util.test_dsc('Test SFTP Backup Storage Update Infomation: password, hostname, sshPort, username')

#====================== Password ======================
    test_util.test_dsc('Update Password')
    res_ops.update_sftp_info(sftp_backup_storage_uuid, 'password', 'zstackmevoco')
    exception_catch = 0
    try:
        host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid, timeout=recnt_timeout) 
    except:
        exception_catch = 1
    finally:
        if exception_catch == 0:
           test_util.test_fail('not catch the exception, but shuold not reconnect sftp after updating the password of sftp') 
        elif exception_catch == 1:
            test_util.test_dsc('catch the exception, cannot reconnect sftp after updating the password of sftp')

    test_util.test_dsc('Update Sftp Host Password')
    cmd = 'echo "zstackmevoco"| passwd --stdin root'
    os.system(cmd)
    host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid, timeout=recnt_timeout)   

    test_util.test_dsc('Recover Sftp Host Password')
    res_ops.update_sftp_info(sftp_backup_storage_uuid, 'password', 'password')
    cmd = 'echo "password"| passwd --stdin root'
    os.system(cmd)

#====================== Port ======================
    test_util.test_dsc('Update sshPort')
    res_ops.update_sftp_info(sftp_backup_storage_uuid, 'sshPort', '23')
    exception_catch = 0
    try:
        host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid, timeout=recnt_timeout)
    except:
        exception_catch = 1
    finally:
        if exception_catch == 0:
           test_util.test_fail('not catch the exception, but shuold not reconnect sftp after updating the sshPort of sftp')
        elif exception_catch == 1:
            test_util.test_dsc('catch the exception, cannot reconnect sftp after updating the sshPort of sftp')

    test_util.test_dsc('Update Sftp Host SSH Port')
    cmd = 'sed -i \'/#Port 22/ i Port 23\' /etc/ssh/sshd_config'
    os.system(cmd)
    cmd = 'service sshd restart'
    os.system(cmd)
    host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid, timeout=recnt_timeout)

    test_util.test_dsc('Recover Sftp Host SSH Port')
    res_ops.update_sftp_info(sftp_backup_storage_uuid, 'sshPort', '22')
    cmd = 'sed -i \'/Port 23/d\' /etc/ssh/sshd_config'
    os.system(cmd)
    cmd = 'service sshd restart'
    os.system(cmd)

#====================== hostname ======================
    test_util.test_dsc('Update Hostname')
    test_util.test_dsc('Create New VM as Sftp')
    vm = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm)

    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
#    ssh.make_ssh_no_password(vm_ip, test_lib.lib_get_vm_username(vm_inv), \
#            test_lib.lib_get_vm_password(vm_inv))
#    test_stub.copy_id_dsa(vm_inv, ssh_cmd, tmp_file)
#    test_stub.copy_id_dsa_pub(vm_inv)

#    cmd = '%s "mkdir /home/sftpBackupStorage" ' % (ssh_cmd)
#    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)

#    res_ops.update_sftp_info(sftp_backup_storage_uuid, 'hostname', vm_ip)
#    host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid, timeout=recnt_timeout)

    test_util.test_dsc('Recover Sftp Hostname')
    res_ops.update_sftp_info(sftp_backup_storage_uuid, 'hostname', sftp_backup_storage_hostname)
    host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid, timeout=recnt_timeout)

#====================== username ======================

    vm.destroy()
    test_obj_dict.rm_vm(vm)

    test_util.test_pass('SFTP Backup Storage Update Infomation SUCCESS')

#Will be called only if exception happens in test().
def error_cleanup():
    global sftp_backup_storage_uuid
    global sftp_backup_storage_hostname
    test_lib.lib_error_cleanup(test_obj_dict)
    res_ops.update_sftp_info(sftp_backup_storage_uuid, 'password', 'password')
    cmd = 'echo "password"| passwd --stdin root'
    os.system(cmd)
    res_ops.update_sftp_info(sftp_backup_storage_uuid, 'sshPort', '22')
    cmd = 'sed -i \'/Port 23/d\' /etc/ssh/sshd_config'
    os.system(cmd)
    cmd = 'service sshd restart'
    os.system(cmd)
    res_ops.update_sftp_info(sftp_backup_storage_uuid, 'hostname', sftp_backup_storage_hostname)
    host_ops.reconnect_sftp_backup_storage(sftp_backup_storage_uuid, timeout=recnt_timeout)
