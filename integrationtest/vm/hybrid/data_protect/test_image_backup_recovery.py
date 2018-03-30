# -*- coding: UTF-8 -*-
'''

New Integration Test for data protect under hybrid.

@author: Glody 
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
disaster_bs_uuid = None
root_volume_uuid = None

def test():
    global disaster_bs_uuid
    global root_volume_uuid
    disaster_bs_dict = bs_ops.get_disaster_backup_storage_info(test_lib.deploy_config)
    name = disaster_bs_dict['name']
    description = disaster_bs_dict['description']
    hostname = disaster_bs_dict['hostname']
    url = disaster_bs_dict['url']
    username = disaster_bs_dict['username']
    password = disaster_bs_dict['password']
    sshport = disaster_bs_dict['port']
    #AddDisasterImageStoreBackupStorage
    disaster_backup_storage = bs_ops.add_disaster_image_store_bs(url, hostname, username, password, sshport, name, description)
    disaster_bs_uuid = disaster_backup_storage.uuid
    #AttachBackupStorageToZone
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    bs_ops.attach_backup_storage(disaster_bs_uuid, zone_uuid)
    #Selete a candidate image to sync
    cond = res_ops.gen_query_conditions('name', '=', 'sftp')
    local_bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', 'other')
    image_uuid_local = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    #SyncImageFromImageStoreBackupStorage 
    disaster_bs_image = img_ops.sync_image_from_image_store_backup_storage(disaster_bs_uuid, local_bs_uuid, image_uuid_local)
    #Check the process status when syncing image
    cond = res_ops.gen_query_conditions('resourceUuid', '=', local_bs_uuid)
    system_tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0].tag
    status = system_tag.split('::')[7]
    if status not in ['running', 'success']:
        test_util.test_fail('Error status for recovery image, status: %s' %status)
    #Check if the image's media_type correct
    disaster_bs_image_uuid = disaster_bs_image.uuid
    cond = res_ops.gen_query_conditions('uuid', '=', disaster_bs_image_uuid)
    media_type = res_ops.query_resource(res_ops.IMAGE, cond)[0].mediaType
    if media_type != 'RootVolumeTemplate':
        test_util.test_fail('Wrong image type, the expect is "RootVolumeTemplate", the real is "%s"' %media_type) 
    #Check if the system tag of the image in disaster bs is 'remote'
    cond = res_ops.gen_query_conditions('resourceUuid', '=', disaster_bs_image_uuid)
    system_tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0]
    if system_tag.tag != "remote":
        test_util.test_fail("Here isn't 'remote' system tag for image in data protect bs")
    #Check if GetImagesFromImageStoreBackupStorage works well
    #disaster_bs_image_lst = img_ops.get_images_from_image_store_backup_storage(disaster_bs_uuid)
    #if disaster_bs_image_lst.infos == []:
    #    test_util.test_fail('GetImagesFromImageStoreBackupStorage unable to list the images in disaster bs')
    #Try to sync the same image again, it's negative test
    try:
        image_uuid = img_ops.sync_image_from_image_store_backup_storage(disaster_bs_uuid, local_bs_uuid, image_uuid_local)
    except Exception,e:
        if unicode(e).encode("utf-8").find('包含') != -1:
            test_util.test_logger('Try to sync the image which had exist in disaster bs get the error info expectly: %s' %unicode(e).encode("utf-8"))
    else:
        test_util.test_fail('Try to sync the image which had exist in local bs success unexpectly')
    #Delete local image and recovery from disaster bs
    img_ops.delete_image(image_uuid_local)
    recovery_image = img_ops.recovery_image_from_image_store_backup_storage(local_bs_uuid, disaster_bs_uuid, disaster_bs_image_uuid, 'other')
    image_uuid_recovery = recovery_image.uuid
    #Check the process status when recoverying image
    cond = res_ops.gen_query_conditions('resourceUuid', '=', local_bs_uuid)
    system_tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0].tag
    status = system_tag.split('::')[7]
    if status not in ['running', 'success']:
        test_util.test_fail('Error status for recovery image, status: %s' %status)
    #Check if recovery image success
    if recovery_image.backupStorageRefs[0].backupStorageUuid != local_bs_uuid:
        test_util.test_fail('Recovery image failed, image uuid is %s' %recovery_image.uuid)
    if recovery_image.mediaType != 'RootVolumeTemplate':
        test_util.test_fail('Wrong image media type after recovery, the expect is "RootVolumeTemplate", the real is "%s"' %media_type)
 
    try:
        #Try to recovery the same image again, it's negative test
        recovery_image = img_ops.recovery_image_from_image_store_backup_storage(local_bs_uuid, disaster_bs_uuid, disaster_bs_image_uuid)
        image_uuid_recovery = recovery_image.uuid
    except Exception,e:
        if unicode(e).encode("utf-8").find('包含') != -1:
            test_util.test_pass('Try to recovery the image which had exist in local bs get the error info expectly: %s' %unicode(e).encode("utf-8"))
    else:
        test_util.test_fail('Try to recovery the image which had exist in local bs success unexpectly')
    cond = res_ops.gen_query_conditions('backupStorageRefs.backupStorageUuid', '=', disaster_bs_uuid)
    disaster_bs_images = res_ops.query_resource(res_ops.IMAGE, cond)
    for img in disaster_bs_images:
        img_ops.delete_image(img.uuid)
    #Check for feature ZSTAC-6709 image delete strategy
    #disaster_bs_image_lst = img_ops.get_images_from_image_store_backup_storage(disaster_bs_uuid)
    #if disaster_bs_image_lst.infos != []:
    #    test_util.test_fail('Delete all images in disaster bs but GetImagesFromImageStoreBackupStorage still does not  null')
    test_util.test_pass('Test image sync and recovery success')

#Will be called only if exception happens in test().
def error_cleanup():
    global disaster_bs_uuid
    global root_volume_uuid
    vol_ops.delete_volume(root_volume_uuid)
    if disaster_bs_uuid != None:
        bs_ops.delete_backup_storage(disaster_bs_uuid)
    
#recover envrionment wehether the test pass or not
def env_recover():
    global disaster_bs_uuid
    if disaster_bs_uuid != None:
        bs_ops.delete_backup_storage(disaster_bs_uuid)

