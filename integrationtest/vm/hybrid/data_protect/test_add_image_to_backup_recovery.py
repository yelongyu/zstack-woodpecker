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

def test():
    global dpbs_uuid
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

    cond = res_ops.gen_query_conditions('name', '=', 'image_store_bs')
    local_bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid
    cond = res_ops.gen_query_conditions('backupStorageRefs.backupStorageUuid', '=', local_bs_uuid)
    image = res_ops.query_resource(res_ops.IMAGE, cond)[0]

    image_option = test_util.ImageOption()
    image_option.set_name('add_image_to_data_protect_bs')
    image_option.set_format(image.format)
    image_option.set_platform(image.platform)
    image_option.set_url(image.url)
    image_option.set_mediaType(image.mediaType)
    image_option.set_backup_storage_uuid_list([dpbs_uuid])
    try:
        new_img = img_ops.add_image(image_option)
    except Exception,e:
        if str(e).find('forbidden') != -1:
            test_util.test_pass('AddImage is forbidden in Disaster BS, Here is the expect error info: %s' %str(e))

    finally:
        bs_ops.delete_backup_storage(dpbs_uuid)

    test_util.test_fail('The Image is add to Disaster BS unexpectly')

#Will be called only if exception happens in test().
def error_cleanup():
    global dpbs_uuid
    if dpbs_uuid != None:
        bs_ops.delete_backup_storage(dpbs_uuid)
    
