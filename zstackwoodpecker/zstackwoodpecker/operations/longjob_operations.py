'''

All long job operations for test.

@author: Legion
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import apibinding.inventory as inventory


def submit_longjob(job_name, job_data, name=None, target_resource_uuid=None, session_uuid=None):
    action = api_actions.SubmitLongJobAction()
    action.jobName = job_name
    action.jobData = job_data
    action.name = name
    action.targetResourceUuid = target_resource_uuid
    test_util.action_logger('Submit Long Job {Name: %s, Job_Name: %s, Job_Data: %s, Target_Resource_Uuid: %s}' % (name, job_name, job_data, target_resource_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventory

def get_task_progress(api_id, session_uuid=None):
    action = api_actions.GetTaskProgressAction()
    action.apiId = api_id
    test_util.action_logger('Get task [apiId: %s] progress' % api_id)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def cancel_longjob(uuid, systemTags=None, timeout=None, userTags=None, session_uuid=None):
    action = api_actions.CancelLongJobAction()
    action.uuid = uuid
    action.systemTags = systemTags
    action.timeout = timeout
    action.userTags = userTags
    test_util.action_logger('Cancel job [uuid: %s]' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventories

def rerun_longjob(uuid, session_uuid = None):
    action = api_actions.RerunLongJobAction()
    action.uuid = uuid
    test_util.action_logger('Rerun longjob [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory
