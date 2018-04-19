# -*- coding: UTF-8 -*-
import os
'''

New Integration Test for data volume backup to and recovery from disaster bs.

@author: Glody 
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os

test_stub = test_lib.lib_get_test_stub()
disaster_bs_uuid = None
data_volume_uuid = None
image_uuid = None

def test():
    global disaster_bs_uuid
    global data_volume_uuid
    global image_uuid
    disasterBsUrls = os.environ.get('disasterBsUrls')
    name = 'disaster_bs'
    description = 'backup storage for disaster'
    url = '/zstack_bs'
    sshport = 22
    hostname = disasterBsUrls.split('@')[1]
    username = disasterBsUrls.split(':')[0]
    password = disasterBsUrls.split('@')[0].split(':')[1]
    test_util.test_logger('Disaster bs server hostname is %s, username is %s, password is %s' %(hostname, username, password))
    #AddDisasterImageStoreBackupStorage
    disaster_backup_storage = bs_ops.add_disaster_image_store_bs(url, hostname, username, password, sshport, name, description)
    disaster_bs_uuid = disaster_backup_storage.uuid
    #AttachBackupStorageToZone
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    bs_ops.attach_backup_storage(disaster_bs_uuid, zone_uuid)
    #Create data volume
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('nfsPrimaryStorageName'))
    primary_storage_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0].uuid
    disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('imageStoreBackupStorageName'))
    local_bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid
    volume_option = test_util.VolumeOption()
    volume_option.set_disk_offering_uuid(disk_offering_uuid)
    volume_option.set_name('data_volume_for_data_protect_test')
    volume_option.set_primary_storage_uuid(primary_storage_uuid)
    data_volume = vol_ops.create_volume_from_offering(volume_option)
    #CreateDataVolumeTemplateFromVolume
    data_volume_uuid = data_volume.uuid 
    image_option = test_util.ImageOption()
    image_option.set_data_volume_uuid(data_volume_uuid)
    image_option.set_name('create_data_iso_to_image_store')
    image_option.set_backup_storage_uuid_list([disaster_bs_uuid])
    image = img_ops.create_data_volume_template(image_option)
    disaster_bs_image_uuid = image.uuid
    #Check if the image's media_type correct
    cond = res_ops.gen_query_conditions('uuid', '=', disaster_bs_image_uuid)
    media_type = res_ops.query_resource(res_ops.IMAGE, cond)[0].mediaType
    if media_type != 'DataVolumeTemplate':
        test_util.test_fail('Wrong image media type, the expect is "DataVolumeTemplate", the real is "%s"' %media_type) 
    #Check if create data volume with volume template success
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('nfsPrimaryStorageName'))
    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0].uuid
    new_volume = vol_ops.create_volume_from_template(disaster_bs_image_uuid, ps_uuid)
    vol_ops.delete_volume(new_volume.uuid)
    #Check if the system tag of the image in disaster bs is 'remote' 
    cond = res_ops.gen_query_conditions('resourceUuid', '=', disaster_bs_image_uuid)
    system_tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0]
    if system_tag.tag != "remote":
        test_util.test_fail("Here isn't 'remote' system tag for image in data protect bs")
    #Check recovery data volume
    recovery_image = img_ops.recovery_image_from_image_store_backup_storage(local_bs_uuid, disaster_bs_uuid, disaster_bs_image_uuid) 
    #Check the process status when recoverying image
    cond = res_ops.gen_query_conditions('resourceUuid', '=', local_bs_uuid)
    system_tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0].tag
    status = system_tag.split('::')[7]
    if status not in ['running', 'success']:
        test_util.test_fail('Error status for recovery image, status: %s' %status)
    #Check if recovery data volume success
    if recovery_image.backupStorageRefs[0].backupStorageUuid != local_bs_uuid:
        test_util.test_fail('Recovery image failed, image uuid is %s' %recovery_image.uuid)
    if recovery_image.mediaType != 'DataVolumeTemplate':
        test_util.test_fail('Wrong image media type after recovery, the expect is "DataVolumeTemplate", the real is "%s"' %media_type)
    image_uuid = recovery_image.uuid

    try:
        #Try to recovery the same image again, it's negative test
        recovery_image = img_ops.recovery_image_from_image_store_backup_storage(local_bs_uuid, disaster_bs_uuid, disaster_bs_image_uuid)
    except Exception,e:
        if unicode(e).encode("utf-8").find('包含') != -1:
            test_util.test_pass('Try to recovery the same image again and get the error info expectly: %s' %unicode(e).encode("utf-8"))
    finally: 
        vol_ops.delete_volume(data_volume_uuid)
        img_ops.delete_image(image_uuid)
    test_util.test_fail('Try to recovery the same image second time success unexpectly')

#Will be called only if exception happens in test().
def error_cleanup():
    global disaster_bs_uuid
    global data_volume_uuid
    global image_uuid
    vol_ops.delete_volume(data_volume_uuid)
    img_ops.delete_image(image_uuid)
    if disaster_bs_uuid != None:
        bs_ops.delete_backup_storage(disaster_bs_uuid)
    
#recover envrionment wehether the test pass or not
def env_recover():
    global disaster_bs_uuid
    if disaster_bs_uuid != None:
        bs_ops.delete_backup_storage(disaster_bs_uuid)
