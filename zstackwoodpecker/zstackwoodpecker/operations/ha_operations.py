'''

All zstack ha operations

@author: quarkonics
'''
import os

import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import account_operations
import zstackwoodpecker.test_util as test_util

def get_vm_instance_ha_level(uuid, session_uuid = None):
    action = api_actions.GetVmInstanceHaLevelAction()
    action.uuid = uuid
    test_util.action_logger('Get VM instance ha level, uuid: %s' \
            % (uuid))
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result.level

def set_vm_instance_ha_level(uuid, level, session_uuid = None):
    action = api_actions.SetVmInstanceHaLevelAction()
    action.uuid = uuid
    action.level = level
    test_util.action_logger('Set VM instance ha level: %s, uuid: %s' \
            % (level, uuid))
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result

def del_vm_instance_ha_level(uuid, session_uuid = None):
    action = api_actions.DeleteVmInstanceHaLevelAction()
    action.uuid = uuid
    test_util.action_logger('Delete VM instance ha level, uuid: %s' \
            % (uuid))
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result
