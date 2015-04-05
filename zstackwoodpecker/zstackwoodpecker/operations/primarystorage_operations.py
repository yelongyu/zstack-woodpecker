'''

All primary_storage operations for test.

@author: Youyk
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import apibinding.inventory as inventory

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

def attach_primary_storage(primary_storage_uuid, cluster_uuid, session_uuid=None):
    action = api_actions.AttachPrimaryStorageToClusterAction()
    action.clusterUuid = cluster_uuid
    action.primaryStorageUuid = primary_storage_uuid
    action.timeout = 30000
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
