'''

All NAS operations for test.

@author: Legion
'''

from apibinding.api import ApiError
import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations


def add_aliyun_nas_access_group(datacenter_uuid, group_name, session_uuid=None):
    action = api_actions.AddAliyunNasAccessGroupAction()
    action.dataCenterUuid = datacenter_uuid
    action.groupName = group_name
    test_util.action_logger('Add [Aliyun NAS access group:] %s' % group_name)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun nas access group:] %s is added.' % group_name)
    return evt.inventory

def get_aliyun_nas_access_group_remote(datacenter_uuid, session_uuid=None):
    action = api_actions.GetAliyunNasAccessGroupRemoteAction()
    action.dataCenterUuid = datacenter_uuid
    test_util.action_logger('Get [Aliyun nas access group remote:] %s' % datacenter_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def create_aliyun_nas_access_group(datacenter_uuid, group_name, network_type='classic', session_uuid=None):
    action = api_actions.CreateAliyunNasAccessGroupAction()
    action.dataCenterUuid = datacenter_uuid
    action.name = group_name
    action.networkType = network_type
    test_util.action_logger('Create [Aliyun NAS access group:] %s' % group_name)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun nas access group:] %s is created.' % group_name)
    return evt.inventory

def delete_aliyun_nas_access_group(uuid, session_uuid=None):
    action = api_actions.DeleteAliyunNasAccessGroupAction()
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun nas access group:] %s is created.' % uuid)
    return evt.inventory

def create_aliyun_nas_access_group_rule(access_group_uuid, source_cidr, rw_type, session_uuid=None):
    action = api_actions.CreateAliyunNasAccessGroupRuleAction()
    action.accessGroupUuid = access_group_uuid
    action.sourceCidrIp = source_cidr
    action.rwAccessType = rw_type
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun nas access group rule with source cidr:] %s is created.' % source_cidr)
    return evt.inventory

def delete_aliyun_nas_access_group_rule(uuid, session_uuid=None):
    action = api_actions.DeleteAliyunNasAccessGroupRuleAction()
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun nas access group rule:] %s is deleted.' % uuid)
    return evt.inventory

def query_aliyun_nas_access_group(condition=[], session_uuid=None):
    action = api_actions.QueryAliyunNasAccessGroupAction()
    action.conditions = condition
    test_util.action_logger('Query Aliyun Access Group')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def add_aliyun_nas_file_system(datacenter_uuid, fsid, name, session_uuid=None):
    action = api_actions.AddAliyunNasFileSystemAction()
    action.dataCenterUuid = datacenter_uuid
    action.fileSystemId = fsid
    action.name = name
    test_util.action_logger('Add [Aliyun NASFile System:] %s %s' % (name, fsid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun NASFile System:] %s %s is added.' % (name, fsid))
    return evt.inventory

def create_aliyun_nas_file_system(datacenter_uuid, name, storage_type, protocol='NFS', session_uuid=None):
    action = api_actions.CreateAliyunNasFileSystemAction()
    action.dataCenterUuid = datacenter_uuid
    action.storageType = storage_type
    action.protocol = protocol
    action.name = name
    test_util.action_logger('Create [Aliyun NASFile System:] %s %s' % (protocol, storage_type))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun NASFile System:] %s %s is added.' % (protocol, storage_type))
    return evt.inventory

def get_aliyun_nas_file_system_remote(datacenter_uuid, session_uuid=None):
    action = api_actions.GetAliyunNasFileSystemRemoteAction()
    action.dataCenterUuid = datacenter_uuid
    test_util.action_logger('Get [Aliyun nasFile System remote:] %s' % datacenter_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def query_nas_file_system(condition=[], session_uuid=None):
    action = api_actions.QueryNasFileSystemAction()
    action.conditions = condition
    test_util.action_logger('Query NASFile System')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def update_nas_file_system(uuid, description=None, name=None, session_uuid=None):
    action = api_actions.UpdateNasFileSystemAction()
    action.uuid = uuid
    action.description = description
    action.name = name
    test_util.action_logger('Update [NASFile System:] %s %s' % (name, description))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun NASFile System:] %s %s is updated.' % (name, description))
    return evt.inventory

def delete_nas_file_system(uuid, session_uuid=None):
    action = api_actions.DeleteNasFileSystemAction()
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[NASFile System:] %s is deleted.' % uuid)
    return evt.inventory

def add_aliyun_nas_mount_target(nas_fs_uuid, mount_domain, name, session_uuid=None):
    action = api_actions.AddAliyunNasMountTargetAction()
    action.nasFSUuid = nas_fs_uuid
    action.mountDomain = mount_domain
    action.name = name
    test_util.action_logger('Add [Aliyun NAS mount target:] %s %s' % (nas_fs_uuid, mount_domain))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun NAS mount target:] %s %s is added.' % (nas_fs_uuid, mount_domain))
    return evt.inventory

def get_aliyun_nas_mount_target_remote(nas_fs_uuid, session_uuid=None):
    action = api_actions.GetAliyunNasMountTargetRemoteAction()
    action.nasFSUuid = nas_fs_uuid
    test_util.action_logger('Get [Aliyun NAS Mount Target remote:] %s' % nas_fs_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def create_aliyun_nas_mount_target(nas_access_roupUuid, nas_fs_uuid, name, session_uuid=None):
    action = api_actions.CreateAliyunNasMountTargetAction()
    action.nasAccessGroupUuid = nas_access_roupUuid
    action.nasFSUuid = nas_fs_uuid
    action.name = name
    test_util.action_logger('Create [Aliyun NAS Mount Target:] %s %s' % (name, nas_fs_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun NASFile System:] %s %s is added.' % (name, nas_fs_uuid))
    return evt.inventory

def query_nas_mount_target(condition=[], session_uuid=None):
    action = api_actions.QueryNasMountTargetAction()
    action.conditions = condition
    test_util.action_logger('Query NAS Mount Target')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def delete_nas_mount_target(uuid, session_uuid=None):
    action = api_actions.DeleteNasFileSystemAction()
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[NAS Mount Target:] %s is deleted.' % uuid)
    return evt.inventory

def update_nas_mount_target(uuid, description=None, name=None, session_uuid=None):
    action = api_actions.UpdateNasMountTargetAction()
    action.uuid = uuid
    action.description = description
    action.name = name
    test_util.action_logger('Update [NASFile System:] %s %s' % (name, description))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun NASFile System:] %s %s is updated.' % (name, description))
    return evt.inventory

def update_aliyun_nas_mount_target(uuid, description=None, name=None, session_uuid=None):
    action = api_actions.UpdateAliyunMountTargetAction()
    action.uuid = uuid
    action.description = description
    action.name = name
    test_util.action_logger('Update [NASFile System:] %s %s' % (name, description))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun NASFile System:] %s %s is updated.' % (name, description))
    return evt.inventory
