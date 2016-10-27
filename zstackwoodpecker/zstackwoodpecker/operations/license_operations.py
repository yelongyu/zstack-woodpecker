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
