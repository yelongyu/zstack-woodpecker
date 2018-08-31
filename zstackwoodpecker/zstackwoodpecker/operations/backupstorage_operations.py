'''

All backupstorage operations for test.

@author: Youyk
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import apibinding.inventory as inventory

def create_backup_storage(backup_storage_option, session_uuid=None):
    if backup_storage_option.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
        return create_ceph_backup_storage(backup_storage_option, session_uuid=None)
    elif hasattr(inventory, 'IMAGE_STORE_BACKUP_STORAGE_TYPE') and backup_storage_option.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
        return create_image_store_backup_storage(backup_storage_option, session_uuid = None)
    elif backup_storage_option.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
        return create_sftp_backup_storage(backup_storage_option, session_uuid=None)

def create_sftp_backup_storage(backup_storage_option, session_uuid=None):
    action = api_actions.AddSftpBackupStorageAction()
    action.timeout = 300000
    action.name = backup_storage_option.get_name()
    action.description = backup_storage_option.get_description()
    action.type = backup_storage_option.get_type()
    action.url = backup_storage_option.get_url()
    action.hostname = backup_storage_option.get_hostname()
    action.username = backup_storage_option.get_username()
    action.password = backup_storage_option.get_password()
    action.sshPort = backup_storage_option.get_sshPort()
    action.resourceUuid = backup_storage_option.get_resource_uuid()
    action.importImages = backup_storage_option.get_import_images()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Sftp Backup Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def create_image_store_backup_storage(backup_storage_option, session_uuid=None):
    action = api_actions.AddImageStoreBackupStorageAction()
    action.timeout = 300000
    action.name = backup_storage_option.get_name()
    action.description = backup_storage_option.get_description()
    action.type = backup_storage_option.get_type()
    action.url = backup_storage_option.get_url()
    action.hostname = backup_storage_option.get_hostname()
    action.username = backup_storage_option.get_username()
    action.password = backup_storage_option.get_password()
    action.sshPort = backup_storage_option.get_sshPort()
    action.resourceUuid = backup_storage_option.get_resource_uuid()
    action.importImages = backup_storage_option.get_import_images()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Sftp Backup Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def create_ceph_backup_storage(backup_storage_option, session_uuid=None):
    action = api_actions.AddCephBackupStorageAction()
    action.timeout = 300000
    action.name = backup_storage_option.get_name()
    action.description = backup_storage_option.get_description()
    action.type = backup_storage_option.get_type()
    action.monUrls = backup_storage_option.get_monUrls()
    action.imageCachePoolName = \
            backup_storage_option.get_imageCachePoolName()
    action.dataVolumePoolName = \
            backup_storage_option.get_dataVolumePoolName()
    action.rootVolumePoolName = \
            backup_storage_option.get_rootVolumePoolName()
    action.resourceUuid = backup_storage_option.get_resource_uuid()
    action.importImages = backup_storage_option.get_import_images()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Ceph Backup Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def delete_backup_storage(backup_storage_uuid, session_uuid=None):
    '''
    Delete BS will delete all images
    '''
    action = api_actions.DeleteBackupStorageAction()
    action.uuid = backup_storage_uuid
    action.timeout = 6000000
    test_util.action_logger('Delete Backup Storage [uuid:] %s' % backup_storage_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def attach_backup_storage(backup_storage_uuid, zone_uuid, session_uuid=None):
    action = api_actions.AttachBackupStorageToZoneAction()
    action.zoneUuid = zone_uuid
    action.backupStorageUuid = backup_storage_uuid
    action.timeout = 30000
    test_util.action_logger('Attach Backup Storage [uuid:] %s to Zone [uuid:] %s' % \
            (backup_storage_uuid, zone_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def detach_backup_storage(backup_storage_uuid, zone_uuid, \
        session_uuid=None):
    action = api_actions.DetachBackupStorageFromZoneAction()
    action.zoneUuid = zone_uuid
    action.backupStorageUuid = backup_storage_uuid
    action.timeout = 300000
    test_util.action_logger('Detach Backup Storage [uuid:] %s from Zone [uuid:] %s' % \
            (backup_storage_uuid, zone_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_backup_storage_state(backup_storage_uuid, state, session_uuid=None):
    # ENABLE = 'enable'
    # DISABLE = 'disable'
    action = api_actions.ChangeBackupStorageStateAction()
    action.uuid = backup_storage_uuid
    action.stateEvent = state
    action.timeout = 300000
    test_util.action_logger('Change BackupStorageStateAction [uuid:] %s to [state:] %s' % (backup_storage_uuid, state))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_image_store_backup_storage_info(backup_storage_uuid, infoType, infoValue, session_uuid = None):
    action = api_actions.UpdateImageStoreBackupStorageAction()
    action.uuid = backup_storage_uuid
    if infoType == 'password':
        action.password = infoValue
    elif infoType == 'hostname':
        action.hostname = infoValue
    elif infoType == 'sshPort':
        action.sshPort = infoValue
    elif infoType == 'username':
        action.username = infoValue
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def update_sftp_backup_storage_info(sftpUuid, infoType, infoValue, session_uuid = None):
    action = api_actions.UpdateSftpBackupStorageAction()
    action.uuid = sftpUuid
    if infoType == 'password':
        action.password = infoValue
    elif infoType == 'hostname':
        action.hostname = infoValue
    elif infoType == 'sshPort':
        action.sshPort = infoValue
    elif infoType == 'username':
        action.username = infoValue
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt


def reconnect_backup_storage(backup_storage_uuid, session_uuid=None):
    '''
    Reconnect backup storage
    '''
    action = api_actions.ReconnectBackupStorageAction()
    action.uuid = backup_storage_uuid
    action.timeout = 6000000
    test_util.action_logger('Reconnect Backup Storage [uuid:] %s' % backup_storage_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_disaster_backup_storage_info(deploy_config):
    disaster_bs_info = {}
    disaster_bs = deploy_config.zones.zone.disasterBackupStorages.imageStoreBackupStorage
    disaster_bs_info['name'] = disaster_bs.name_
    disaster_bs_info['description'] = disaster_bs.description_
    disaster_bs_info['url'] = disaster_bs.url_
    disaster_bs_info['username'] = disaster_bs.username_
    disaster_bs_info['password'] = disaster_bs.password_
    disaster_bs_info['hostname'] = disaster_bs.hostname_
    disaster_bs_info['port'] = disaster_bs.port_
    return disaster_bs_info

def add_disaster_image_store_bs(url, hostname, username, password, sshport=None, name=None, description=None, end_point=None, attach_point=None, session_uuid=None):
    action = api_actions.AddDisasterImageStoreBackupStorageAction()
    action.hostname = hostname
    action.username = username
    action.password = password
    action.url = url
    if name != None:
        action.name = name
    else:
        action.name = "disaster_image_store"
    if description != None:
        action.description = description
    if sshport != None:
        action.sshPort = sshport
    else:
        action.sshPort = 22
    if end_point != None:
        action.endPoint = end_point
    if attach_point != None:
        action.attachPoint = attach_point
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Disaster ImageStore Backup Storage] %s is added' %action.name )
    return evt.inventory
