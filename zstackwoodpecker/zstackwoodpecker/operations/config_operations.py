'''

All zstack config operations

@author: Youyk
'''
import os

import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import account_operations
import zstackwoodpecker.test_util as test_util

def get_global_config_value(category, name, session_uuid = None, \
        default_value = None):
    value = None
    action = api_actions.QueryGlobalConfigAction()
    action.category = category
    action.conditions = [{'name': 'name', 'op': '=', 'value': name}]
    test_util.action_logger('Get global config category: %s, name: %s' \
            % (category, name))
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    if result:
        if default_value != None and default_value:
            return result[0].defaultValue
        else:
            return result[0].value

def get_global_config_default_value(category, name, session_uuid = None):
    value = None
    return get_global_config_value(category, name, session_uuid, True)

def change_global_config(category, name, value, session_uuid = None):
    default_value = get_global_config_default_value(category, name, session_uuid)
    pre_value = get_global_config_value(category, name, session_uuid)
    action = api_actions.UpdateGlobalConfigAction()
    action.category = category
    action.name = name
    action.defaultValue = str(default_value)
    if value:
        action.value = str(value)
    test_util.action_logger('change global config category: %s, name: %s, to %s' % (category, name, value))
    account_operations.execute_action_with_session(action, session_uuid)

    return pre_value

def change_cluster_config(category, name, value, resourceUuid, session_uuid = None):
    action = api_actions.UpdateResourceConfigAction()
    action.category = category
    action.name = name
    action.value = value
    action.resourceUuid = resourceUuid
    if value:
        action.value = str(value)
    test_util.action_logger('change cluster config category: %s, name: %s, to %s' % (category, name, value))
    account_operations.execute_action_with_session(action, session_uuid)

def query_cluster_config(conditions, session_uuid = None):
    action = api_actions.QueryResourceConfigAction()
    action.conditions = conditions

    test_util.action_logger('query cluster config category %s' % conditions)
    account_operations.execute_action_with_session(action, session_uuid)

def get_cluster_config(category, name, resourceUuid = None, session_uuid = None):
    action = api_actions.GetResourceConfigAction()
    action.category = category
    action.name = name
    action.resourceUuid = resourceUuid
    test_util.action_logger('query cluster config category: %s, name: %s, to %s' % (category, name, resourceUuid))
    ret = account_operations.execute_action_with_session(action, session_uuid)
    return ret.effectiveConfigs

def delete_cluster_config(category, name, resourceUuid = None, session_uuid = None):
    action = api_actions.DeleteResourceConfigAction()
    action.category = category
    action.name = name
    action.resourceUuid = resourceUuid
    test_util.action_logger('query cluster config category: %s, name: %s, to %s' % (category, name, resourceUuid))
    ret = account_operations.execute_action_with_session(action, session_uuid)
    return ret.effectiveConfigs
