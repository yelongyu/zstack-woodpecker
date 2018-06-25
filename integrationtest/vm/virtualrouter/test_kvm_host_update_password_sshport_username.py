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
    global kvm_host_uuid
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    if res_ops.query_resource(res_ops.HOST, conditions):
        kvm_host = res_ops.query_resource(res_ops.HOST, conditions)[0]
        kvm_host_uuid = kvm_host.uuid
    else:
        test_util.test_skip("There is no host. Skip test")

    test_util.test_dsc('Test KVM Host Infomation: password, sshPort, username')

#====================== Password ======================
    test_util.test_dsc('Update Password')
    host_ops.update_kvm_host(kvm_host_uuid, 'password', 'zstackmevoco')
    exception_catch = 0
    try:
        host_ops.reconnect_host(kvm_host_uuid)
    except:
        exception_catch = 1
    finally:
        if exception_catch == 0:
           test_util.test_fail('not catch the exception, but shuold fail to reconnect KVM host after updating the password of KVM host') 
        elif exception_catch == 1:
            test_util.test_dsc('catch the exception, cannot reconnect KVM host after updating the password of KVM host')

    test_util.test_dsc('Update KVM Host Password')
    cmd = 'echo "zstackmevoco"| passwd --stdin root'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd)
    host_ops.reconnect_host(kvm_host_uuid)

    test_util.test_dsc('Recover KVM Host Password')
    host_ops.update_kvm_host(kvm_host_uuid, 'password', 'password')
    cmd = 'echo "password"| passwd --stdin root'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","zstackmevoco",cmd)

#====================== sshPort ======================
    test_util.test_dsc('Update sshPort')
    host_ops.update_kvm_host(kvm_host_uuid, 'sshPort', '23')
    exception_catch = 0
    try:
        host_ops.reconnect_host(kvm_host_uuid)
    except:
        exception_catch = 1
    finally:
        if exception_catch == 0:
           test_util.test_fail('not catch the exception, but shuold fail to reconnect KVM host after updating the sshPort of KVM host')
        elif exception_catch == 1:
            test_util.test_dsc('catch the exception, cannot reconnect KVM host after updating the sshPort of KVM host')

    test_util.test_dsc('Update KVM Host SSH Port')
    cmd = 'sed -i \'/#Port 22/ i Port 23\' /etc/ssh/sshd_config'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd) 
    cmd = 'service sshd restart'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd) 
    host_ops.reconnect_host(kvm_host_uuid)

    test_util.test_dsc('Recover KVM Host SSH Port')
    host_ops.update_kvm_host(kvm_host_uuid, 'sshPort', '22')
    cmd = 'sed -i \'/Port 23/d\' /etc/ssh/sshd_config'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd, port=23)
    cmd = 'service sshd restart'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd, port=23)

#====================== username ======================
    test_util.test_dsc('Update Username')
    host_ops.update_kvm_host(kvm_host_uuid, 'username', 'test')
    exception_catch = 0
    try:
        host_ops.reconnect_host(kvm_host_uuid)
    except:
        exception_catch = 1
    finally:
        if exception_catch == 0:
           test_util.test_fail('not catch the exception, but shuold fail to reconnect KVM host after updating the username of KVM host')
        elif exception_catch == 1:
            test_util.test_dsc('catch the exception, cannot reconnect KVM host after updating the username of KVM host')

    test_util.test_dsc('Update KVM Host username')
    cmd = 'adduser test'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd)
    cmd = 'echo "password"| passwd --stdin test'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd)
    cmd = 'echo "test        ALL=(ALL)       NOPASSWD: ALL">>/etc/sudoers '
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd)
    host_ops.reconnect_host(kvm_host_uuid)

    test_util.test_dsc('Recover KVM Host username')
    host_ops.update_kvm_host(kvm_host_uuid, 'username', 'root')
    cmd = 'userdel test'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd)

    test_util.test_pass('KVM Host Update Infomation SUCCESS')

#Will be called only if exception happens in test().
def error_cleanup():
    global kvm_host_uuid
    host_ops.update_kvm_host(kvm_host_uuid, 'password', 'password')
    cmd = 'echo "password"| passwd --stdin root'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd)

    host_ops.update_kvm_host(kvm_host_uuid, 'sshPort', '22')    
    cmd = 'sed -i \'/Port 23/d\' /etc/ssh/sshd_config'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd)
    cmd = 'service sshd restart'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd)

    host_ops.update_kvm_host(kvm_host_uuid, 'username', 'root')
    cmd = 'userdel test'
    test_lib.lib_execute_ssh_cmd(kvm_host.managementIp,"root","password",cmd)

    host_ops.reconnect_host(kvm_host_uuid)

    test_lib.lib_error_cleanup(test_obj_dict)
