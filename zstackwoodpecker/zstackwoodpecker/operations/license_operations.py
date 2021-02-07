'''

All zstack license operations

@author: Quarkonics
'''
import os

import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import account_operations
import zstackwoodpecker.test_util as test_util

def get_license_info(session_uuid = None):
    action = api_actions.GetLicenseInfoAction()
    test_util.action_logger('Get license info')
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result

def reload_license(session_uuid = None):
    action = api_actions.ReloadLicenseAction()
    test_util.action_logger('Reload license')
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result

def update_license(node_uuid, file_license, session_uuid = None):
    action = api_actions.UpdateLicenseAction()
    action.managementNodeUuid = node_uuid
    action.license = file_license
    test_util.action_logger('update license from UI')
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result


def get_license_addons_info(session_uuid = None):
    action = api_actions.GetLicenseAddOnsAction()
    test_util.action_logger('Get license addons info')
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result

def delete_license(node_uuid, uuid, session_uuid = None):
    action = api_actions.DeleteLicenseAction()
    action.managementNodeUuid = node_uuid
    action.uuid = uuid
    test_util.action_logger('delete license [uuid:] %s' % uuid)
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result

