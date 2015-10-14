'''

Tag related operations

@author: Youyk
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import apibinding.inventory as inventory

def create_system_tag(resourceType, resourceUuid, tag, session_uuid=None):
    action = api_actions.CreateSystemTagAction()
    action.timeout = 30000
    action.resourceType = resourceType
    action.resourceUuid = resourceUuid
    action.tag = tag
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create System Tag [uuid:] %s for [tag:] %s' % \
            (evt.inventory.uuid, tag))
    return evt.inventory

def create_user_tag(resourceType, resourceUuid, tag, session_uuid=None):
    action = api_actions.CreateUserTagAction()
    action.timeout = 30000
    action.resourceType = resourceType
    action.resourceUuid = resourceUuid
    action.tag = tag
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create User Tag [uuid:] %s for [tag:] %s' % \
            (evt.inventory.uuid, tag))
    return evt.inventory

def delete_tag(tag_uuid, session_uuid=None):
    action = api_actions.DeleteTagAction()
    action.uuid = tag_uuid
    action.timeout = 30000
    test_util.action_logger('Delete Tag [uuid:] %s' % tag_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def update_system_tag(tag_uuid, tag, session_uuid = None):
    action = api_actions.UpdateSystemTagAction()
    action.uuid = tag_uuid
    action.tag = tag
    test_util.action_logger('Update Tag [uuid:] %s to %s' % (tag_uuid, tag))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

