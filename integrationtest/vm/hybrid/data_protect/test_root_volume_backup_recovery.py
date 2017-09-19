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
vm = None

def test():
    global dpbs_uuid
    global root_volume_uuid
    global image_uuid
    global vm
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

    cond = res_ops.gen_query_conditions('system', '=', False)
    l3network_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].uuid
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', 'ttylinux')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    vm_option = test_util.VmOption()
    vm_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_option.set_name('vm_for_data_protect_test')
    vm_option.set_l3_uuids([l3network_uuid])
    vm_option.set_image_uuid(image_uuid)
    vm = vm_ops.create_vm(vm_option)

    root_volume_uuid = vm.rootVolumeUuid 
    image_option = test_util.ImageOption()
    image_option.set_root_volume_uuid(root_volume_uuid)
    image_option.set_name('create_root_image_to_image_store')
    image_option.set_backup_storage_uuid_list([dpbs_uuid])
    image = img_ops.create_root_volume_template(image_option)
    image_uuid = image.uuid

    cond = res_ops.gen_query_conditions('uuid', '=', image_uuid)
    media_type = res_ops.query_resource(res_ops.IMAGE, cond)[0].mediaType
    if media_type != 'RootVolumeTemplate':
        test_util.test_fail('Wrong image type, the expect is "RootVolumeTemplate", the real is "%s"' %media_type) 

    recovery_image = img_ops.recovery_image_from_image_store_backup_storage(local_bs_uuid, dpbs_uuid, image_uuid) 
    if recovery_image.backupStorageRefs[0].backupStorageUuid != local_bs_uuid:
        test_util.test_fail('Recovery image failed, image uuid is %s' %recovery_image.uuid)
    if recovery_image.mediaType != 'RootVolumeTemplate':
        test_util.test_fail('Wrong image type after recovery, the expect is "RootVolumeTemplate", the real is "%s"' %recovery_image.mediaType)
    image_uuid = recovery_image.uuid

    vol_ops.delete_volume(root_volume_uuid)
    vm.delete()
    img_ops.delete_image(image_uuid)
    bs_ops.delete_backup_storage(dpbs_uuid) 
    test_util.test_pass('Data volume backup to and recovery from image store backup storage success')

#Will be called only if exception happens in test().
def error_cleanup():
    global dpbs_uuid
    global root_volume_uuid
    global image_uuid
    global vm
    vm.delete()
    vol_ops.delete_volume(root_volume_uuid)
    img_ops.delete_image(image_uuid)
    if dpbs_uuid != None:
        bs_ops.delete_backup_storage(dpbs_uuid)
    
