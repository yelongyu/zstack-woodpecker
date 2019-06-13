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

def create_scheduler_job(name, description, target_uuid, type, parameters, session_uuid = None):
    action = api_actions.CreateSchedulerJobAction()
    action.name = name
    action.description = description
    action.targetResourceUuid = target_uuid
    action.type = type
    action.parameters = parameters
    test_util.action_logger('Create [Scheduler Job:] %s [%s] %s' % (name, target_uuid, type))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Scheduler Job:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def create_scheduler_job_group(name, description, type, parameters, session_uuid = None):
    action = api_actions.CreateSchedulerJobGroupAction()
    action.name = name
    action.description = description
    action.type = type
    action.parameters = parameters
    test_util.action_logger('Create [Scheduler Job Group:] %s %s' % (name, type))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Scheduler Job Group:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def del_scheduler_job(uuid, session_uuid = None):
    action = api_actions.DeleteSchedulerJobAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Scheduler Job:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Scheduler Job:] %s is deleted.' % uuid)

def del_scheduler_job_group(uuid, session_uuid = None):
    action = api_actions.DeleteSchedulerJobGroupAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Scheduler Job Group:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Scheduler Job Group:] %s is deleted.' % uuid)

def create_scheduler_trigger(name, start_time = None, repeat_count = None, interval = None, type = None, cron = None, session_uuid = None):
    action = api_actions.CreateSchedulerTriggerAction()
    action.name = name
    action.startTime = start_time
    action.repeatCount = repeat_count
    action.schedulerInterval = interval
    action.schedulerType = type
    action.cron = cron 
    test_util.action_logger('Create [Scheduler Trigger:] %s [%s] %s %s' % (name, start_time, repeat_count, interval))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Scheduler Trigger:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def del_scheduler_trigger(uuid, session_uuid = None):
    action = api_actions.DeleteSchedulerTriggerAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Scheduler Trigger:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Scheduler Trigger:] %s is deleted.' % uuid)

def add_scheduler_job_to_trigger(trigger_uuid, job_uuid, session_uuid = None):
    action = api_actions.AddSchedulerJobToSchedulerTriggerAction()
    action.schedulerTriggerUuid = trigger_uuid
    action.schedulerJobUuid = job_uuid
    test_util.action_logger('Add [Scheduler Job:] %s to [Scheduler Trigger:] %s ' % (job_uuid, trigger_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Scheduler Job:] %s is added to [Scheduler Trigger:] %s.' % (job_uuid, trigger_uuid))

def add_scheduler_job_group_to_trigger(trigger_uuid, group_uuid, triggerNow = False, session_uuid = None):
    action = api_actions.AddSchedulerJobGroupToSchedulerTriggerAction()
    action.schedulerTriggerUuid = trigger_uuid
    action.schedulerJobGroupUuid = group_uuid
    action.triggerNow = triggerNow
    test_util.action_logger('Add [Scheduler Job Group:] %s to [Scheduler Trigger:] %s ' % (group_uuid, trigger_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Scheduler Job:] %s is added to [Scheduler Trigger:] %s.' % (group_uuid, trigger_uuid))

def remove_scheduler_job_from_trigger(trigger_uuid, job_uuid, session_uuid = None):
    action = api_actions.RemoveSchedulerJobFromSchedulerTriggerAction()
    action.schedulerTriggerUuid = trigger_uuid
    action.schedulerJobUuid = job_uuid
    test_util.action_logger('Remove [Scheduler Job:] %s from [Scheduler Trigger:] %s ' % (job_uuid, trigger_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 

def remove_scheduler_job_group_from_trigger(trigger_uuid, job_group_uuid, session_uuid = None):
    action = api_actions.RemoveSchedulerJobGroupFromSchedulerTriggerAction()
    action.schedulerTriggerUuid = trigger_uuid
    action.schedulerJobGroupUuid = job_group_uuid
    test_util.action_logger('Remove [Scheduler Job:] %s from [Scheduler Trigger:] %s ' % (job_group_uuid, trigger_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)

def delete_scheduler(uuid, session_uuid = None):
    action = api_actions.DeleteSchedulerAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Scheduler:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Scheduler:] %s is deleted.' % uuid)
    return evt

def update_scheduler(uuid, name, parameters, session_uuid = None):
    action = api_actions.UpdateSchedulerAction()
    action.uuid = uuid
    action.name = name
    action.parameters = parameters

    test_util.action_logger('Update [Scheduler:] %s [name:] %s [parameters:] %s ' \
                    % (uuid, name, parameters))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Scheduler:] %s is updated.' % uuid)
    return evt

def update_scheduler_job_group(uuid, name, parameters, state = "Enabled", session_uuid = None):
    action = api_actions.UpdateSchedulerJobGroupAction()
    action.uuid = uuid
    action.name = name
    action.parameters = parameters
    action.state = state

    test_util.action_logger('Update [Scheduler Job Group:] %s [name:] %s [parameters:] %s [state:] %s' \
                    % (uuid, name, parameters, state))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Scheduler Job Group:] %s is updated.' % uuid)
    return evt

def update_scheduler_trigger(uuid, name, interval=None, start=None, repeat=None, cron=None, session_uuid = None):
    action = api_actions.UpdateSchedulerTriggerAction()
    action.uuid = uuid
    action.name = name
    action.schedulerInterval = interval
    action.repeatCount = repeat
    action.startTime = start
    action.cron = cron
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Update [Scheduler Trigger:] %s [name:] %s [schedulerInterval:] %s [repeatCount:] %s \
                        [startTime:] %s [cron:] %s' \
                        % (uuid, name, schedulerInterval, repeatCount, startTime, cron))
    return evt

def change_scheduler_state(uuid, state, session_uuid = None):
    action = api_actions.ChangeSchedulerStateAction()
    action.uuid = uuid
    action.stateEvent = state
    test_util.action_logger('Change [Scheduler:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Scheduler:] %s is changed to %s.' % (uuid, state))
    return evt

def get_current_time(session_uuid = None):
    action = api_actions.GetCurrentTimeAction()
    test_util.action_logger('GetCurrentTime')
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt

def query_db_backup(condition = [], uuid = None, name = None, session_uuid = None):
    action = api_actions.QueryDatabaseBackupAction()
    action.conditions = condition
    action.uuid = uuid
    action.name = name
    test_util.action_logger('QueryDatabaseBackup')
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt

def get_db_backup_from_imagestore(url, session_uuid = None):
    action = api_actions.GetDatabaseBackupFromImageStoreAction()
    action.url = url
    test_util.action_logger('GetDatabaseBackupFromImageStore')
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt

def export_db_backup_from_bs(backupStorageUuid, databaseBackupUuid, session_uuid = None):
    action = api_actions.ExportDatabaseBackupFromBackupStorageAction()
    action.backupStorageUuid = backupStorageUuid
    action.databaseBackupUuid = databaseBackupUuid
    test_util.action_logger('ExportDatabaseBackupFromBackupStorage')
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt

def recover_db_from_backup(uuid = None, mysqlRootPassword = None, backupStorageUrl = None, backupInstallPath = None, session_uuid = None):
    action = api_actions.RecoverDatabaseFromBackupAction()
    action.uuid = uuid
    action.mysqlRootPassword = mysqlRootPassword
    action.backupStorageUrl = backupStorageUrl
    action.backupInstallPath = backupInstallPath
    test_util.action_logger('RecoverDatabaseFromBackup')
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt

def sync_db_from_imagestore_bs(dstBackupStorageUuid, srcBackupStorageUuid, uuid, session_uuid = None):
    action = api_actions.SyncDatabaseBackupFromImageStoreBackupStorageAction()
    action.dstBackupStorageUuid = dstBackupStorageUuid
    action.srcBackupStorageUuid = srcBackupStorageUuid
    action.uuid = uuid
    test_util.action_logger('SyncDatabaseBackupFromImageStoreBackupStorage')
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt

def add_jobs_to_job_group(jobs_uuid, group_uuid, session_uuid = None):
    action = api_actions.AddSchedulerJobsToSchedulerJobGroupAction()
    action.schedulerJobGroupUuid = group_uuid
    action.schedulerJobUuids = jobs_uuid
    test_util.action_logger('AddSchedulerJobsToSchedulerJobGroup')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def remove_jobs_from_job_group(jobs_uuid, group_uuid, session_uuid = None):
    action = api_actions.RemoveSchedulerJobsFromSchedulerJobGroupAction()
    action.schedulerJobGroupUuid = group_uuid
    action.schedulerJobUuids = jobs_uuid
    test_util.action_logger('RemoveSchedulerJobsFromSchedulerJobGroup')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def run_scheduler_trigger(uuid, job_uuids, session_uuid = None):
    action = api_actions.RunSchedulerTriggerAction()
    action.uuid = uuid
    action.jobUuids = job_uuids
    test_util.action_logger('RunSchedulerTriggerAction')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt
