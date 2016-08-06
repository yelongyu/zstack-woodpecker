'''

All scheduler operations for test.

@author: quarkonics
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import config_operations

import os
import inspect

def delete_scheduler(uuid, session_uuid = None):
    action = api_actions.DeleteAccountAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Scheduler:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Scheduler:] %s is deleted.' % uuid)
    return evt
