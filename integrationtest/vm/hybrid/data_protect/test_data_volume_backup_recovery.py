'''

New Integration Test for data protect under hybrid.

@author: Glody 
'''

import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
dpbs_uuid = None
data_volume = None
image = None
def test():
    global dpbs_uuid
    global data_volume
    global image
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
    cond = res_ops.gen_query_conditions('zone.host.managementIp', '=', host_ip)
    local_bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid

    volume_option = test_util.VolumeOption()
    volume_option.set_disk_offering_uuid(disk_offering_uuid)
    volume_option.set_name('data_volume_for_data_protect_test')
    volume_option.set_primary_storage_uuid(primary_storage_uuid)
    data_volume = vol_ops.create_volume_from_offering(volume_option)

    data_volume_uuid = data_volume.uuid 
    image_option = test_util.ImageOption()
    image_option.set_data_volume_uuid(data_volume_uuid)
    image_option.set_name('create_data_iso_to_image_store')
    image_option.set_backup_storage_uuid_list([dpbs_uuid])
    image = img_ops.create_data_volume_template(image_option)

    cond = res_ops.gen_query_conditions('uuid', '=', image.uuid)
    media_type = res_ops.query_resource(res_ops.IMAGE, cond)[0].mediaType
    if media_type != 'DataVolumeTemplate':
        test_util.test_fail('Wrong image media type, the expect is "DataVolumeTemplate", the real is "%s"' %media_type) 

    recovery_image = img_ops.recovery_image_from_image_store_backup_storage(local_bs_uuid, dpbs_uuid, image.uuid) 
    if recovery_image.backupStorageRefs[0].backupStorageUuid != local_bs_uuid:
        test_util.test_fail('Recovery image failed, image uuid is %s' %recovery_image.uuid)

    data_volume.delete()
    image.delete()
    bs_ops.delete_backup_storage(dpbs_uuid) 
    test_util.test_pass('Data volume backup to and recovery from image store backup storage success')

#Will be called only if exception happens in test().
def error_cleanup():
    global dpbs_uuid
    global data_volume
    global image
    data_volume.delete()
    image.delete()
    if dpbs_uuid != None:
        bs_ops.delete_backup_storage(dpbs_uuid)
    
