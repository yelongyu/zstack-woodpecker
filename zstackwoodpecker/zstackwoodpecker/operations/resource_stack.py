'''

All Stack template operations for test.

@author: Lei Liu
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations

def create_resource_stack(resource_stack_option):
    action = api_actions.CreateResourceStackAction()
    name = resource_stack_option.get_name()
    if not name:
        action.name = 'test_stack_template_default_name'
    else:
        action.name = name

    action.templateContent = resource_stack_option.get_templateContent()
    action.zoneUuid = resource_stack_option.get_zone_uuid()
    action.description = resource_stack_option.get_description()
    action.rollback = resource_stack_option.get_rollback()
    action.templateContent = resource_stack_option.get_templateContent()
    action.templateUuid = resource_stack_option.get_template_uuid()
    action.parameters = resource_stack_option.get_parameters()

    evt = account_operations.execute_action_with_session(action, resource_stack_option.get_session_uuid())
    return evt.inventory

def preview_resource_stack(resource_stack_option, session_uuid):
    action = api_actions.PreviewResourceStackAction()
    action.type = resource_stack_option.get_type()
    action.parameters = resource_stack_option.get_parameters()
    action.templateContent = resource_stack_option.get_parameters()
    action.uuid = resource_stack_option.get_uuid()
    test_util.action_logger('Preview Resource Stack template')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_resource_stack(uuid, session_uuid=None):
    action = api_actions.DeleteResourceStackAction()
    action.uuid = uuid
    action.timeout = 240000
    test_util.action_logger('Delete resource stack [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_resource_from_resource_stack(uuid, session_uuid=None):
    action = api_actions.GetResourceFromResourceStackAction()
    action.uuid = uuid
    test_util.action_logger('get resource from resource stack [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def query_event_from_resource_stack(uuid, session_uuid=None):
    action = api_actions.QueryEventFromResourceStackAction()
    action.uuid = uuid
    test_util.action_logger('query event from resource stack [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def restart_resource_stack(uuid, session_uuid=None):
    action = api_actions.RestartResourceStackAction()
    action.uuid = uuid
    test_util.action_logger('restart resource stack [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory
