'''

All primary_storage operations for test.

@author: Youyk
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import apibinding.inventory as inventory

def create_primary_storage(primary_storage_option, session_uuid=None):
    if primary_storage_option.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:
        return create_ceph_primary_storage(primary_storage_option, session_uuid=None)
    return create_nfs_primary_storage(primary_storage_option, session_uuid=None)

def create_nfs_primary_storage(primary_storage_option, session_uuid=None):
    action = api_actions.AddNfsPrimaryStorageAction()
    action.timeout = 30000
    action.name = primary_storage_option.get_name()
    action.description = primary_storage_option.get_description()
    action.type = primary_storage_option.get_type()
    action.url = primary_storage_option.get_url()
    action.zoneUuid = primary_storage_option.get_zone_uuid()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Primary Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def create_local_primary_storage(primary_storage_option, session_uuid=None):
    action = api_actions.AddLocalPrimaryStorageAction()
    action.timeout = 30000
    action.name = primary_storage_option.get_name()
    action.description = primary_storage_option.get_description()
    action.type = primary_storage_option.get_type()
    action.url = primary_storage_option.get_url()
    action.zoneUuid = primary_storage_option.get_zone_uuid()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Primary Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def add_mon_to_ceph_primary_storage(mon_urls, ceph_ps_uuid, system_tag=None, user_tag=None, session_uuid=None):
    action = api_actions.AddMonToCephPrimaryStorageAction()
    action.timeout = 300000
    action.monUrls = mon_urls
    action.uuid = ceph_ps_uuid
    action.systemTags = system_tag
    action.userTags = user_tag
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Add Mon To Ceph Primary Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def remove_mon_from_ceph_primary_storage(mon_hostnames, ceph_ps_uuid, system_tag=None, user_tag=None, session_uuid=None):
    action = api_actions.RemoveMonFromCephBackupStorageAction()
    action.timeout = 300000
    action.monHostnames = mon_hostnames
    action.uuid = ceph_ps_uuid
    action.systemTags = system_tag
    action.userTags = user_tag
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Add Mon To Ceph Primary Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def create_ceph_primary_storage(primary_storage_option, session_uuid=None):
    action = api_actions.AddCephPrimaryStorageAction()
    action.timeout = 300000
    action.name = primary_storage_option.get_name()
    action.description = primary_storage_option.get_description()
    action.type = primary_storage_option.get_type()
    action.monUrls = primary_storage_option.get_monUrls()
    action.imageCachePoolName = \
            primary_storage_option.get_imageCachePoolName()
    action.dataVolumePoolName = \
            primary_storage_option.get_dataVolumePoolName()
    action.rootVolumePoolName = \
            primary_storage_option.get_rootVolumePoolName()
    action.zoneUuid = primary_storage_option.get_zone_uuid()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Primary Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def add_ceph_primary_storage_pool(primary_storage_uuid, pool_name, aliasName=None, isCreate=None, resourceUuid=None, poolType="Root", description=None, session_uuid=None):
    action = api_actions.AddCephPrimaryStoragePoolAction()
    action.timeout = 300000
    action.primaryStorageUuid = primary_storage_uuid
    action.poolName = pool_name
    action.aliasName = aliasName
    action.description = description
    action.isCreate = isCreate
    action.type = poolType
    action.resourceUuid = resourceUuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Primary Storage [uuid:] %s Pool [uuid:] %s [name:] %s' % \
            (action.primaryStorageUuid, evt.inventory.uuid, action.poolName))
    return evt.inventory


def create_sharedblock_primary_storage(primary_storage_option, disk_uuid, session_uuid=None):
    action = api_actions.AddSharedBlockGroupPrimaryStorageAction()
    action.timeout = 300000
    action.name = primary_storage_option.get_name()
    action.zoneUuid = primary_storage_option.get_zone_uuid()
    action.description = primary_storage_option.get_description()
    action.diskUuids = disk_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create SharedBlock Primary Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory


def delete_primary_storage(primary_storage_uuid, session_uuid=None):
    '''
    Delete PS will delete all VMs and Volumes using this ps.
    '''
    action = api_actions.DeletePrimaryStorageAction()
    action.uuid = primary_storage_uuid
    action.timeout = 600000
    test_util.action_logger('Delete Primary Storage [uuid:] %s' % primary_storage_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_ceph_primary_storage_pool(primary_storage_pool_uuid, session_uuid=None):
    '''
    Delete PS Pool will delete all Volumes using this ps.
    '''
    action = api_actions.DeleteCephPrimaryStoragePoolAction()
    action.uuid = primary_storage_pool_uuid
    action.timeout = 600000
    test_util.action_logger('Delete Primary Storage Pool [uuid:] %s' % primary_storage_pool_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory


def attach_primary_storage(primary_storage_uuid, cluster_uuid, session_uuid=None):
    action = api_actions.AttachPrimaryStorageToClusterAction()
    action.clusterUuid = cluster_uuid
    action.primaryStorageUuid = primary_storage_uuid
    action.timeout = 300000
    test_util.action_logger('Attach Primary Storage [uuid:] %s to Cluster [uuid:] %s' % \
            (primary_storage_uuid, cluster_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def detach_primary_storage(primary_storage_uuid, cluster_uuid, \
        session_uuid=None):
    '''
    Detach PS will stop all VMs using this volume.
    '''
    action = api_actions.DetachPrimaryStorageFromClusterAction()
    action.clusterUuid = cluster_uuid
    action.primaryStorageUuid = primary_storage_uuid
    action.timeout = 300000
    test_util.action_logger('Detach Primary Storage [uuid:] %s from Cluster [uuid:] %s' % \
            (primary_storage_uuid, cluster_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_primary_storage_state(primary_storage_uuid, state, session_uuid=None):
    action = api_actions.ChangePrimaryStorageStateAction()
    action.uuid = primary_storage_uuid
    action.stateEvent = state
    action.timeout = 300000
    test_util.action_logger('Change Primary Storage [uuid:] %s to [state:] %s' \
            % (primary_storage_uuid, state))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def cleanup_imagecache_on_primary_storage(primary_storage_uuid, session_uuid=None):
    action = api_actions.CleanUpImageCacheOnPrimaryStorageAction()
    action.uuid = primary_storage_uuid
    action.timeout = 300000
    test_util.action_logger('Cleanup Imagecache on Primary Storage [uuid:] %s' \
            % (primary_storage_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def reconnect_primary_storage(primary_storage_uuid, session_uuid=None):
    '''
    Reconnect primary storage
    '''
    action = api_actions.ReconnectPrimaryStorageAction()
    action.uuid = primary_storage_uuid
    action.timeout = 6000000
    test_util.action_logger('Reconnect Primary Storage [uuid:] %s' % primary_storage_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_trash_on_primary_storage(primary_storage_uuid, session_uuid=None):
    action = api_actions.GetTrashOnPrimaryStorageAction()
    action.uuid = primary_storage_uuid
    action.timeout = 6000000
    test_util.action_logger('Get Trash On Primary Storage [uuid:] %s' % primary_storage_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def clean_up_trash_on_primary_storage(primary_storage_uuid, trash_id=None, session_uuid=None):
    action = api_actions.CleanUpTrashOnPrimaryStorageAction()
    action.uuid = primary_storage_uuid
    action.trashId = trash_id
    action.timeout = 6000000
    test_util.action_logger('Clean Up Trash On Primary Storage [uuid:] %s' % primary_storage_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt
