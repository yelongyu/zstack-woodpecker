'''

New Integration Test for add images to disaster backup storage. It is a negative test

@author: Glody 
'''

import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
disaster_bs_uuid = None

def test():
    global disaster_bs_uuid
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
    #get a candidate image
    cond = res_ops.gen_query_conditions('name', '=', 'sftp')
    local_bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid
    cond = res_ops.gen_query_conditions('backupStorageRefs.backupStorageUuid', '=', local_bs_uuid)
    image = res_ops.query_resource(res_ops.IMAGE, cond)[0]
    #setup image option
    image_option = test_util.ImageOption()
    image_option.set_name('add_image_to_data_protect_bs')
    image_option.set_format(image.format)
    image_option.set_platform(image.platform)
    image_option.set_url(image.url)
    image_option.set_mediaType(image.mediaType)
    image_option.set_backup_storage_uuid_list([disaster_bs_uuid])
    #Try to add image to disaster bs directly
    try:
        new_img = img_ops.add_image(image_option)
    except Exception,e:
        if str(e).find('forbidden') != -1:
            test_util.test_pass('AddImage is forbidden in Disaster BS, Here is the expect error info: %s' %str(e))

    finally:
        bs_ops.delete_backup_storage(disaster_bs_uuid)

    test_util.test_fail('The Image is add to Disaster BS unexpectly')

#Will be called only if exception happens in test().
def error_cleanup():
    global disaster_bs_uuid
    if disaster_bs_uuid != None:
        bs_ops.delete_backup_storage(disaster_bs_uuid)

#recover envrionment wehether the test pass or not
def env_recover():
    global disaster_bs_uuid
    if disaster_bs_uuid != None:
        bs_ops.delete_backup_storage(disaster_bs_uuid)

