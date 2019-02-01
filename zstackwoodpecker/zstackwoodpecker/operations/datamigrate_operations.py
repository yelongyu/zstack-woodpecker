'''

All data migrate operations for test.

@author: Legion
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import apibinding.inventory as inventory


def ps_migrage_volume(dst_ps_uuid, vol_uuid, volume_type=None, session_uuid=None):
    action = api_actions.PrimaryStorageMigrateVolumeAction()
    action.dstPrimaryStorageUuid = dst_ps_uuid
    action.volumeUuid = vol_uuid
    action.timeout = 7200000
    test_util.action_logger('Migrate [%s Volume: %s] to [Primary Storage: %s]' % (volume_type, vol_uuid, dst_ps_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventory

def ps_migrage_root_volume(dst_ps_uuid, vol_uuid, session_uuid=None):
    evt_inv = ps_migrage_volume(dst_ps_uuid=dst_ps_uuid, vol_uuid=vol_uuid, volume_type='Root', session_uuid=session_uuid)
    return evt_inv

def ps_migrage_data_volume(dst_ps_uuid, vol_uuid, session_uuid=None):
    evt_inv = ps_migrage_volume(dst_ps_uuid=dst_ps_uuid, vol_uuid=vol_uuid, volume_type='Data', session_uuid=session_uuid)
    return evt_inv

def bs_migrage_image(dst_bs_uuid, src_bs_uuid, image_uuid, session_uuid=None):
    action = api_actions.BackupStorageMigrateImageAction()
    action.dstBackupStorageUuid = dst_bs_uuid
    action.srcBackupStorageUuid = src_bs_uuid
    action.imageUuid = image_uuid
    test_util.action_logger('Migrate [Image: %s] from [Backup Storage: %s ]to [Backup Storage: %s]' % (image_uuid, src_bs_uuid, dst_bs_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventory

def get_ps_candidate_for_vol_migration(vol_uuid, session_uuid=None):
    action = api_actions.GetPrimaryStorageCandidatesForVolumeMigrationAction()
    action.volumeUuid = vol_uuid
    test_util.action_logger('Get Primary Storage Candidates for Volume Migration')
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def get_bs_candidate_for_image_migration(src_bs_uuid, session_uuid=None):
    action = api_actions.GetBackupStorageCandidatesForImageMigrationAction()
    action.srcBackupStorageUuid = src_bs_uuid
    test_util.action_logger('Get Backup Storage Candidates for Volume Migration')
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

