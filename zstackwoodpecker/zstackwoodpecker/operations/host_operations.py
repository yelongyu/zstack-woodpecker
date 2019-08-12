'''

All host operations for test.

@author: Youyk
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import resource_operations
import apibinding.inventory as inventory
import zstacklib.utils.shell as shell
import time

def add_kvm_host(host_option, session_uuid=None):
    action = api_actions.AddKVMHostAction()
    action.timeout = 300000
    action.clusterUuid = host_option.get_cluster_uuid()
    action.username = host_option.get_username()
    action.password = host_option.get_password()
    action.managementIp = host_option.get_management_ip()
    action.name = host_option.get_name()
    action.description = host_option.get_description()
    action.hostTags = host_option.get_host_tags()
    action.systemTags = host_option.get_system_tags()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Add KVM Host [uuid:] %s with [ip:] %s' % \
            (evt.uuid, action.managementIp))
    return evt.inventory

def delete_host(host_uuid, session_uuid=None):
    action = api_actions.DeleteHostAction()
    action.uuid = host_uuid
    action.timeout = 120000
    test_util.action_logger('Delete Host [uuid:] %s' % host_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def reconnect_host(host_uuid, session_uuid=None, timeout=600000):
    action = api_actions.ReconnectHostAction()
    action.uuid = host_uuid
    action.timeout = timeout
    test_util.action_logger('Reconnect Host [uuid:] %s' % host_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    cur_time = time.time()
    while True:
        cond = resource_operations.gen_query_conditions('uuid', '=', host_uuid)
        host = resource_operations.query_resource_with_num(resource_operations.HOST, cond, limit = 1)[0]
        if host.status == "Connected" or host.status == "Disconnected":
            break
        time.sleep(1)
        if cur_time - time.time() > timeout:
            test_util.test_logger("reconnect_host timeout(%s)" % (timeout))
            break

    return evt.inventory

def reconnect_sftp_backup_storage(sftpbs_uuid, session_uuid=None, timeout=120000):
    action = api_actions.ReconnectSftpBackupStorageAction()
    action.uuid = sftpbs_uuid
    action.timeout = timeout
    test_util.action_logger('Reconnect SFTP Backup Storage [uuid:] %s' % sftpbs_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_host_state(host_uuid, state, session_uuid=None):
    '''
    If change the state to Enabled, it is needed to check the machine's state
    is really changed to connected, before using it. It is because ZStack will
    send reconnect command, when change the host state to enabled. 
    '''
    action = api_actions.ChangeHostStateAction()
    action.uuid = host_uuid
    action.stateEvent = state
    action.timeout = 300000
    test_util.action_logger('Change Host [uuid:] %s to [state:] %s' % (host_uuid, state))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_host(hostUuid, infoType, infoValue, session_uuid = None):
    action = api_actions.UpdateHostAction()
    action.uuid = hostUuid
    if infoType == 'name':
        action.name = infoValue
    elif infoType == 'description':
        action.description = infoValue
    elif infoType == 'managementIp':
        action.managementIp = infoValue
    test_util.action_logger('Update Host %s to %s' %(infoType,infoValue))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_kvm_host(hostUuid, infoType, infoValue, session_uuid = None):
    action = api_actions.UpdateKVMHostAction()
    action.uuid = hostUuid
    if infoType == 'password':
        action.password = infoValue
    elif infoType == 'sshPort':
        action.sshPort = infoValue
    elif infoType == 'username':
        action.username = infoValue
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def get_ept_status(ip, username, password, port):
    ssh_cmd = 'sshpass -p %s ssh -p %s -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null' %(password, port)
    ret1 = shell.call("%s %s@%s cat /etc/modprobe.d/intel-ept.conf|awk -F'=' '{print $2}'" %(ssh_cmd, username, ip)).strip()
    ret2 = shell.call("%s %s@%s cat /sys/module/kvm_intel/parameters/ept" %(ssh_cmd, username, ip)).strip()
    if ret1 == "0" and ret2 == "N":
        return "disable"
    elif ret2 == "Y":
        return "enable"
    else:
        return ret2+ret1

def query_host(conditions, session_uuid = None):
    action = api_actions.QueryHostAction()
    action.conditions = conditions
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def poweroff_host(host_uuids, admin_password, mn_flag=None, session_uuid=None):
    action = api_actions.PowerOffHostAction()
    action.hostUuids = host_uuids 
    action.adminPassword = admin_password 
    action.timeout = 1200000
    evt = account_operations.execute_action_with_session(action, session_uuid, mn_flag=mn_flag)
    return evt
