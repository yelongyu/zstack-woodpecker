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
    action = api_actions.DeleteSchedulerAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Scheduler:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Scheduler:] %s is deleted.' % uuid)
    return evt

def update_scheduler(uuid, type, name, start_date=None, interval=None, repeatCount=None, cron=None, session_uuid = None):
    action = api_actions.UpdateSchedulerAction()
    action.uuid = uuid
    action.schedulerType = type
    action.schedulerName = name
    action.startDate = startDate
    action.schedulerInterval = interval
    action.repeatCount = repeatCount
    action.cronScheduler = cron

    test_util.action_logger('Update [Scheduler:] %s [schdulerType:] % [schdulerName:] %s [startDate:] %s [interval:] %s [repeatCount:] %s [cron:] %s' \
                    % (uuid, type, name, start_date, interval, repeatCount, cron))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Scheduler:] %s is updated.' % uuid)
    return evt
