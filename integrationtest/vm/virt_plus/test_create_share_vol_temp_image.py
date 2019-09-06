'''
Test create shareable volume template image.
Cover bug:ZSTAC-23152
@author: chenyuan.xu
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.ssh as ssh
import os


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create volume and check')
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for i in ps:
        if i.type == 'SharedBlock':
            break
    else:
        test_util.test_skip('Skip test on non sharedblock PS')

    cond = res_ops.gen_query_conditions('type', '=', 'SharedBlock')
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0] 
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('mediumDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi', 'volumeProvisioningStrategy::ThickProvisioning'])
    volume_creation_option.set_primary_storage_uuid(ps.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()

    cond = res_ops.gen_query_conditions('type', '=', 'ImageStoreBackupStorage')
    bs_list = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond) 
    image_option = test_util.ImageOption()
    image_option.set_data_volume_uuid(volume.volume.uuid)
    image_option.set_name('data_resize_template')
    image_option.set_backup_storage_uuid_list([bs_list[0].uuid])
    data_image = img_ops.create_data_volume_template(image_option)
   
    test_util.test_pass('Create Shareable Data Volume Template Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict) 
        
