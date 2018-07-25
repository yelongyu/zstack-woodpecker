'''

Image (Root Volume) Template operations for test.

@author: Youyk
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import resource_operations as res_ops

def add_data_volume_template(image_option):
    action = api_actions.AddImageAction()
    action.name = image_option.get_name()
    action.url = image_option.get_url()
    action.mediaType = 'DataVolumeTemplate'
    if image_option.get_mediaType() and \
            action.mediaType != image_option.get_mediaType():
        test_util.test_warn('image type %s was not %s' % \
                (image_option.get_mediaType(), action.mediaType))

    action.format = image_option.get_format()
    action.backupStorageUuids = image_option.get_backup_storage_uuid_list()
    test_util.action_logger('Add [Volume:] %s from [url:] %s ' % (action.name, action.url))
    evt = account_operations.execute_action_with_session(action, image_option.get_session_uuid())

    test_util.test_logger('[volume:] %s is added.' % evt.inventory.uuid)
    return evt.inventory

def add_image(image_option):
    action = api_actions.AddImageAction()
    action.name = image_option.get_name()
    action.url = image_option.get_url()
    action.mediaType = image_option.get_mediaType()
    action.format = image_option.get_format()
    action.platform = image_option.get_platform()
    action.backupStorageUuids = image_option.get_backup_storage_uuid_list()
    test_util.action_logger('Add [Image:] %s from [url:] %s ' % (action.name, action.url))
    evt = account_operations.execute_action_with_session(action, image_option.get_session_uuid())
    test_util.test_logger('[image:] %s is added.' % evt.inventory.uuid)
    return evt.inventory

def add_iso_template(image_creation_option):
    '''
    Add iso template
    '''
    action = api_actions.AddImageAction()
    action.name = image_creation_option.get_name()
    action.guest_os_type = image_creation_option.get_guest_os_type()
    action.mediaType = 'ISO'

    action.backupStorageUuids = \
            image_creation_option.get_backup_storage_uuid_list()
    action.bits = image_creation_option.get_bits()
    action.description = image_creation_option.get_description()
    action.format = 'iso'
    action.url = image_creation_option.get_url()
    action.timeout = image_creation_option.get_timeout()
    test_util.action_logger('Add ISO Template from url: %s in [backup Storage:] %s' % (action.url, action.backupStorageUuids))
    evt = account_operations.execute_action_with_session(action, \
            image_creation_option.get_session_uuid())
    return evt.inventory

def add_root_volume_template(image_creation_option):
    '''
    Add root volume template
    '''
    action = api_actions.AddImageAction()
    action.name = image_creation_option.get_name()
    action.guest_os_type = image_creation_option.get_guest_os_type()
    action.mediaType = 'RootVolumeTemplate'
    if image_creation_option.get_mediaType() and \
            action.mediaType != image_creation_option.get_mediaType():
        test_util.test_warn('image type %s was not %s' % \
                (image_creation_option.get_mediaType(), action.mediaType))

    action.backupStorageUuids = \
            image_creation_option.get_backup_storage_uuid_list()
    action.bits = image_creation_option.get_bits()
    action.description = image_creation_option.get_description()
    action.format = image_creation_option.get_format()
    if image_creation_option.get_system_tags() != None:
        action.systemTags = image_creation_option.get_system_tags().split(',')
    action.url = image_creation_option.get_url()
    action.timeout = image_creation_option.get_timeout()
    test_util.action_logger('Add Root Volume Template from url: %s in [backup Storage:] %s' % (action.url, action.backupStorageUuids))
    evt = account_operations.execute_action_with_session(action, \
            image_creation_option.get_session_uuid())
    return evt.inventory

def add_root_volume_template_apiid(image_creation_option, apiid):
    '''
    Add root volume template
    '''
    action = api_actions.AddImageAction()
    action.id = apiid
    action.name = image_creation_option.get_name()
    action.guest_os_type = image_creation_option.get_guest_os_type()
    action.mediaType = 'RootVolumeTemplate'
    if image_creation_option.get_mediaType() and \
            action.mediaType != image_creation_option.get_mediaType():
        test_util.test_warn('image type %s was not %s' % \
                (image_creation_option.get_mediaType(), action.mediaType))

    action.backupStorageUuids = \
            image_creation_option.get_backup_storage_uuid_list()
    action.bits = image_creation_option.get_bits()
    action.description = image_creation_option.get_description()
    action.format = image_creation_option.get_format()
    if image_creation_option.get_system_tags() != None:
        action.systemTags = image_creation_option.get_system_tags().split(',')
    action.url = image_creation_option.get_url()
    action.timeout = image_creation_option.get_timeout()
    test_util.action_logger('Add Root Volume Template from url: %s in [backup Storage:] %s' % (action.url, action.backupStorageUuids))
    evt = account_operations.execute_action_with_session(action, \
            image_creation_option.get_session_uuid())
    return evt.inventory

def create_root_volume_template(image_creation_option):
    '''
    Create Root Volume Template from a root volume
    '''
    action = api_actions.CreateRootVolumeTemplateFromRootVolumeAction()
    action.rootVolumeUuid = image_creation_option.get_root_volume_uuid()
    action.backupStorageUuids = image_creation_option.get_backup_storage_uuid_list()

    name = image_creation_option.get_name()
    if not name:
        action.name = 'test_template_image'
    else:
        action.name = name

    action.guestOsType = image_creation_option.get_guest_os_type()
    action.system = image_creation_option.get_system()
    action.platform = image_creation_option.get_platform()
    action.timeout = image_creation_option.get_timeout()

    description = image_creation_option.get_description()
    if not description:
        action.description = "test create template from volume"
    else:
        action.description = description

    test_util.action_logger('Create Image Template from [root Volume:] %s in [backup Storage:] %s' % (action.rootVolumeUuid, action.backupStorageUuids))
    evt = account_operations.execute_action_with_session(action, image_creation_option.get_session_uuid())
    return evt.inventory

def create_data_volume_template(image_creation_option):
    '''
    Create Data Volume Template from a data volume
    '''
    action = api_actions.CreateDataVolumeTemplateFromVolumeAction()
    action.volumeUuid = image_creation_option.get_data_volume_uuid()
    action.backupStorageUuids = image_creation_option.get_backup_storage_uuid_list()

    name = image_creation_option.get_name()
    if not name:
        action.name = 'test_template_image'
    else:
        action.name = name

    description = image_creation_option.get_description()
    if not description:
        action.description = "test create template from volume"
    else:
        action.description = description

    test_util.action_logger('Create Data Volume Template from [data Volume:] %s in [backup Storage:] %s' % (action.volumeUuid, action.backupStorageUuids))
    evt = account_operations.execute_action_with_session(action, image_creation_option.get_session_uuid())
    return evt.inventory

def create_root_volume_template_apiid(image_creation_option, apiid):
    '''
    Create Root Volume Template from a root volume
    '''
    action = api_actions.CreateRootVolumeTemplateFromRootVolumeAction()
    action.id = apiid
    action.rootVolumeUuid = image_creation_option.get_root_volume_uuid()
    action.backupStorageUuids = image_creation_option.get_backup_storage_uuid_list()

    name = image_creation_option.get_name()
    if not name:
        action.name = 'test_template_image'
    else:
        action.name = name

    action.guestOsType = image_creation_option.get_guest_os_type()
    action.system = image_creation_option.get_system()
    action.platform = image_creation_option.get_platform()

    description = image_creation_option.get_description()
    if not description:
        action.description = "test create template from volume"
    else:
        action.description = description

    test_util.action_logger('Create Image Template from [root Volume:] %s in [backup Storage:] %s' % (action.rootVolumeUuid, action.backupStorageUuids))
    evt = account_operations.execute_action_with_session(action, image_creation_option.get_session_uuid())
    return evt.inventory


def delete_image(image_uuid, backup_storage_uuid_list=None, session_uuid=None):
    action = api_actions.DeleteImageAction()
    action.uuid = image_uuid
    action.backupStorageUuids = backup_storage_uuid_list
    test_util.action_logger('Delete [image:] %s' % image_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def expunge_image(image_uuid, backup_storage_uuid_list=None, session_uuid=None):
    action = api_actions.ExpungeImageAction()
    action.imageUuid = image_uuid
    action.backupStorageUuids = backup_storage_uuid_list
    test_util.action_logger('Expunge [image:] %s' % image_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def sync_image_size(image_uuid, session_uuid=None):
    action = api_actions.SyncImageSizeAction()
    action.uuid = image_uuid
    test_util.action_logger('Sync image size [image:] %s' % image_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def create_template_from_snapshot(image_creation_option, session_uuid=None):
    action = api_actions.CreateRootVolumeTemplateFromVolumeSnapshotAction()
    action.snapshotUuid = image_creation_option.get_root_volume_uuid()
    action.backupStorageUuids = image_creation_option.get_backup_storage_uuid_list()

    action.guestOsType = image_creation_option.get_guest_os_type()
    action.system = image_creation_option.get_system()
    action.platform = image_creation_option.get_platform()

    name = image_creation_option.get_name()
    if not name:
        action.name = 'test_template_image_by_snapshot'
    else:
        action.name = name

    description = image_creation_option.get_description()
    if not description:
        action.description = "test create template from snapshot: %s" % \
                action.snapshotUuid
    else:
        action.description = description

    test_util.action_logger('Create Image Template from [snapshot:] %s in [backup Storage:] %s' % (action.snapshotUuid, action.backupStorageUuids))
    evt = account_operations.execute_action_with_session(action, image_creation_option.get_session_uuid())
    return evt.inventory

def create_root_template_from_backup(backupStorageUuid,backupUuid,name=None,session_uuid=None):
    action = api_actions.CreateRootVolumeTemplateFromVolumeBackupAction()
    action.backupStorageUuid = backupStorageUuid
    action.backupUuid = backupUuid
    if not name:
        name = "backup_image_%s" % backupUuid
    action.name = name
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger("Create image from [backup:] %s in [backup Storage:] %s" % (backupUuid, backupStorageUuid))
    return evt.inventory    

def create_data_template_from_backup(backupStorageUuid,backupUuid,name=None,session_uuid=None):
    action = api_actions.CreateDataVolumeTemplateFromVolumeBackupAction()
    action.backupStorageUuid = backupStorageUuid
    action.backupUuid = backupUuid
    if not name:
        name = "backup_image_%s" % backupUuid
    action.name = name
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger("Create image from [backup:] %s in [backup Storage:] %s" % (backupUuid, backupStorageUuid))
    return evt.inventory

def reconnect_sftp_backup_storage(bs_uuid, session_uuid = None):
    action = api_actions.ReconnectSftpBackupStorageAction()
    action.uuid = bs_uuid
    action.timeout = 120000
    test_util.action_logger('Reconnect Sftp Backup Storage [uuid:] %s' % bs_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def commit_volume_as_image(image_creation_option, session_uuid = None):
    action = api_actions.CommitVolumeAsImageAction()
    action.name = image_creation_option.get_name()
    action.volumeUuid = image_creation_option.get_root_volume_uuid()
    action.backupStorageUuids = image_creation_option.get_backup_storage_uuid_list()
    action.guestOsType = image_creation_option.get_guest_os_type()
    action.system = image_creation_option.get_system()
    action.platform = image_creation_option.get_platform()

    description = image_creation_option.get_description()
    if not description:
        action.description = "test commit volume as image"
    else:
        action.description = description

    test_util.action_logger('Commit Image Template from [Volume:] %s in [backup Storage:] %s' % (action.volumeUuid, action.backupStorageUuids))
    evt = account_operations.execute_action_with_session(action, image_creation_option.get_session_uuid())
    return evt.inventory

def commit_volume_as_image_apiid(image_creation_option, apiid, session_uuid = None):
    action = api_actions.CommitVolumeAsImageAction()
    action.id = apiid
    action.name = image_creation_option.get_name()
    action.volumeUuid = image_creation_option.get_root_volume_uuid()
    action.backupStorageUuids = image_creation_option.get_backup_storage_uuid_list()
    action.guestOsType = image_creation_option.get_guest_os_type()
    action.system = image_creation_option.get_system()
    action.platform = image_creation_option.get_platform()

    description = image_creation_option.get_description()
    if not description:
        action.description = "test commit volume as image"
    else:
        action.description = description

    test_util.action_logger('Commit Image Template from [Volume:] %s in [backup Storage:] %s' % (action.volumeUuid, action.backupStorageUuids))
    evt = account_operations.execute_action_with_session(action, image_creation_option.get_session_uuid())
    return evt.inventory

def export_image_from_backup_storage(image_uuid, bs_uuid, session_uuid = None):
    action = api_actions.ExportImageFromBackupStorageAction()
    action.imageUuid = image_uuid
    action.backupStorageUuid = bs_uuid
    #export image need to compose snapshots. This action is costing. 
    action.timeout = 600000
    test_util.action_logger('Export [image:] %s from [Backup Storage:] %s' % (image_uuid, bs_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Image:] %s was exported as [url:] %s' %(image_uuid, evt.imageUrl))
    return evt.imageUrl

def delete_exported_image_from_backup_storage(image_uuid, bs_uuid, session_uuid = None):
    action = api_actions.DeleteExportedImageFromBackupStorageAction()
    action.imageUuid = image_uuid
    action.backupStorageUuid = bs_uuid
    test_util.action_logger('Delete exported [image:] %s from [Backup Storage:] %s' % (image_uuid, bs_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('Exported [image:] %s was deleted from [url:] %s' %(image_uuid, evt.imageUrl))
    return evt

def attach_iso(iso_uuid, vm_uuid, session_uuid = None):
    '''
    Attach iso to vm
    '''
    action = api_actions.AttachIsoToVmInstanceAction()
    action.isoUuid = iso_uuid
    action.vmInstanceUuid = vm_uuid
    test_util.action_logger('Attach ISO[UUID: %s] to VM[UUID: %s]' % (iso_uuid, vm_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def detach_iso(vm_uuid, iso_uuid=None, session_uuid = None):
    '''
    Detach iso from vm
    '''
    action = api_actions.DetachIsoFromVmInstanceAction()
    action.vmInstanceUuid = vm_uuid
    action.isoUuid = iso_uuid
    test_util.action_logger('Detach ISO from VM[UUID: %s]' % (vm_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_image_qga_enable(img_uuid, session_uuid = None):
    action = api_actions.GetImageQgaEnableAction()
    action.uuid = img_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def set_image_qga_enable(img_uuid, session_uuid = None):
    action = api_actions.SetImageQgaAction()
    action.uuid = img_uuid
    action.enable = 'true'
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def set_image_qga_disable(img_uuid, session_uuid = None):
    action = api_actions.SetImageQgaAction()
    action.uuid = img_uuid
    action.enable = 'false'
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def sync_image_from_image_store_backup_storage(dst_bs_uuid, src_bs_uuid, img_uuid, name=None, session_uuid=None):
    action = api_actions.SyncImageFromImageStoreBackupStorageAction()
    action.dstBackupStorageUuid = dst_bs_uuid
    action.srcBackupStorageUuid = src_bs_uuid
    action.uuid = img_uuid
    if name != None:
        action.name = name
    else:
        action.name = 'backup_image'
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def recovery_image_from_image_store_backup_storage(dst_bs_uuid, src_bs_uuid, img_uuid, name=None, session_uuid=None):
    action = api_actions.RecoveryImageFromImageStoreBackupStorageAction()
    action.dstBackupStorageUuid = dst_bs_uuid
    action.srcBackupStorageUuid = src_bs_uuid
    action.uuid = img_uuid
    if name != None:
        action.name = name
    else:
        action.name = 'recovery_image'
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_images_from_image_store_backup_storage(uuid, session_uuid=None):
    action = api_actions.GetImagesFromImageStoreBackupStorageAction()
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def update_image_platform(uuid, platform, session_uuid=None):
    action = api_actions.UpdateImageAction()
    action.uuid = uuid
    action.platform = platform
    test_util.action_logger('Update [image %s] platform' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory   

def change_image_state(uuid, state, session_uuid):
    action = api_actions.ChangeImageStateAction()
    action.uuid = uuid
    action.stateEvent = state
    test_util.action_logger('Change [image %s] state' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory   

