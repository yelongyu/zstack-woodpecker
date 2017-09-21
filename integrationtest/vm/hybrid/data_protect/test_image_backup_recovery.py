'''

New Integration Test for data protect under hybrid.

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
dpbs_uuid = None
root_volume_uuid = None
image_uuid = None

def test():
    global dpbs_uuid
    global root_volume_uuid
    global image_uuid
    vm_res = hyb_ops.get_data_protect_image_store_vm_ip(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
    hostname = vm_res[0]
    url = vm_res[1]
    username = vm_res[2]
    password = vm_res[3]
    sshport = vm_res[4]
    name = "BS-public"
    data_protect_backup_storage = hyb_ops.add_disaster_image_store_bs(url, hostname, username, password, sshport, name)
    dpbs_uuid = data_protect_backup_storage.uuid 
    cond = res_ops.gen_query_conditions('resourceUuid', '=', dpbs_uuid)
    system_tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0]
    if system_tag.tag != "remote":
        test_util.test_fail("Here isn't 'remote' system tag for data protect bs")
    zone = res_ops.query_resource(res_ops.ZONE)[0]
    bs_ops.attach_backup_storage(dpbs_uuid, zone.uuid)

    primary_storage_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
    host_ip = res_ops.query_resource(res_ops.HOST)[0].managementIp
    cond = res_ops.gen_query_conditions('name', '=', 'image_store_bs')
    local_bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid

    cond = res_ops.gen_query_conditions('name', '=', 'ttylinux')
    image_uuid1 = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
  
    dpbs_image = img_ops.sync_image_from_image_store_backup_storage(dpbs_uuid, local_bs_uuid, image_uuid1)
    dpbs_image_uuid = dpbs_image.uuid
    cond = res_ops.gen_query_conditions('uuid', '=', dpbs_image_uuid)
    media_type = res_ops.query_resource(res_ops.IMAGE, cond)[0].mediaType
    if media_type != 'RootVolumeTemplate':
        test_util.test_fail('Wrong image type, the expect is "RootVolumeTemplate", the real is "%s"' %media_type) 

    cond = res_ops.gen_query_conditions('resourceUuid', '=', dpbs_image_uuid)
    system_tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0]
    if system_tag.tag != "remote":
        test_util.test_fail("Here isn't 'remote' system tag for image in data protect bs")
    
    dpbs_image_lst = img_ops.list_image_from_image_store_backup_storage(dpbs_uuid)
    if dpbs_image_lst.infos == []:
        test_util.test_fail('ListImagesFromImageStoreBackupStorage unable to list the images in disaster bs')

    try:
        image_uuid = img_ops.sync_image_from_image_store_backup_storage(dpbs_uuid, local_bs_uuid, image_uuid1)
    except Exception,e:
        if str(e).find('already contains it') != -1:
            test_util.test_logger('Try to sync the image which had exist in disaster bs get the error info expectly: %s' %str(e))
    try:
        recovery_image = img_ops.recovery_image_from_image_store_backup_storage(local_bs_uuid, dpbs_uuid, dpbs_image_uuid)
        image_uuid = recovery_image.uuid
    except Exception,e:
        if str(e).find('already contains it') != -1:
            test_util.test_pass('Try to recovery the image which had exist in local bs get the error info expectly: %s' %str(e))
    finally:
        if image_uuid != None:
            img_ops.delete_image(image_uuid)
        bs_ops.delete_backup_storage(dpbs_uuid) 
    test_util.test_fail('Try to recovery the image which had exist in local bs success unexpectly')

#Will be called only if exception happens in test().
def error_cleanup():
    global dpbs_uuid
    global root_volume_uuid
    global image_uuid
    vol_ops.delete_volume(root_volume_uuid)
    if image_uuid != None:
        img_ops.delete_image(image_uuid)
    if dpbs_uuid != None:
        bs_ops.delete_backup_storage(dpbs_uuid)
    
