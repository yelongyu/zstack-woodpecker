'''

All host operations for test.

@author: Songtao
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import zstackwoodpecker.operations.account_operations as account_operations
import apibinding.inventory as inventory


def get_monitor_item(resourceType, session_uuid=None):
    action = api_actions.GetMonitorItemAction()
    action.timeout = 3000
    action.resourceType = resourceType
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Get %s Monitor Item ' % action.resourceType)
    return evt.inventories

def create_monitor_trigger(resource_uuid, duration, expression, session_uuid=None):
    action = api_actions.CreateMonitorTriggerAction()
    action.targetResourceUuid = resource_uuid
    action.duration = duration
    action.name = resource_uuid
    action.expression = expression
    action.timeout = 6000 
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def query_monitor_trigger(uuid=None, session_uuid=None):
    action = api_actions.QueryMonitorTriggerAction()
    action.uuid = uuid
    action.conditions = []
    action.timeout = 6000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_monitor_trigger(uuid, infoType, infoValue, session_uuid=None):
    action = api_actions.UpdateMonitorTriggerAction()
    action.uuid = uuid
    if infoType == 'name':
        action.name = infoValue
    elif infoType == 'description':
        action.description = infoValue
    elif infoType == 'expression':
        action.expression = infoValue
    elif infoType == 'duration':
        action.duration = infoValue
    action.timeout = 6000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_monitor_trigger(uuid, session_uuid=None):
    action = api_actions.DeleteMonitorTriggerAction()
    action.uuid = uuid
    action.timeout = 6000 
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_monitor_trigger_state(uuid, state, session_uuid=None):
    action = api_actions.ChangeMonitorTriggerStateAction()
    action.uuid = uuid
    action.stateEvent = state
    action.timeout = 6000
    test_util.action_logger('Change monitor trigger [uuid:] %s to [state:] %s' % (uuid, state))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_email_media(name, smtpport, smtpserver, username, password, session_uuid=None):
    action = api_actions.CreateEmailMediaAction()
    action.name = name
    action.smtpPort = smtpport
    action.smtpServer = smtpserver
    action.username = username
    action.password = password
    action.timeout = 6000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def query_email_media(uuid=None, session_uuid=None):
    action = api_actions.QueryMediaAction()
    action.uuid = uuid
    action.timeout = 6000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_email_media_state(uuid, state, session_uuid=None):
    action = api_actions.ChangeMediaStateAction()
    action.uuid = uuid
    action.stateEvent = state
    action.timeout = 6000
    test_util.action_logger('Change email media [uuid:] %s to [state:] %s' % (uuid, state))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_email_media(uuid, session_uuid=None):
    action = api_actions.DeleteMediaAction()
    action.uuid = uuid
    action.timeout = 6000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_email_monitor_trigger_action(name, mediaUuid, triggerUuids, email,session_uuid=None):
    action = api_actions.CreateEmailMonitorTriggerActionAction()
    action.name = name
    action.mediaUuid = mediaUuid
    action.triggerUuids = triggerUuids
    action.email = email
    action.timeout = 6000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory


def query_monitor_trigger_action(uuid=None, session_uuid=None):
    action = api_actions.QueryMonitorTriggerAction()
    action.uuid = uuid
    action.timeout = 6000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventories


def change_monitor_trigger_action_state(uuid, state, session_uuid=None):
    action = api_actions.ChangeMonitorTriggerActionStateAction()
    action.uuid = uuid
    action.state = state
    action.timeout = 6000
    test_util.action_logger('Change monitor trigger action [uuid:] %s to [state:] %s' % (uuid, state))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_monitor_trigger_action(uuid, session_uuid=None):
    action = api_actions.DeleteMonitorTriggerAction()
    action.uuid = uuid
    action.timeout = 6000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory



def attach_monitor_trigger_action_to_trigger(actionUuid, triggerUuid,session_uuid=None):
    action = api_actions.AttachMonitorTriggerActionToTriggerAction()
    action.actionUuid = actionUuid
    action.triggerUuid = triggerUuid
    action.timeout = 6000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def detach_monitor_trigger_action_to_trigger(actionUuid, triggerUuid,session_uuid=None):
    action = api_actions.DetachMonitorTriggerActionFromTriggerAction()
    action.actionUuid = actionUuid
    action.triggerUuid = triggerUuid
    action.timeout = 6000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

