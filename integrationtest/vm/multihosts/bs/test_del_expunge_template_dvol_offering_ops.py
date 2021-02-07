'''
Test for deleting and expunge vol template check vol created from offering ops.

The key step:
-add image1
-create vm1 from image1
-create data vol1
-create template from data vol1
-create data vol2 from template
-delete template
-do data vol all ops test on data vol2
-expunge template
-do data vol all ops test on data vol2

@author: PxChen
'''

import os
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
image1 = None

def test():
    global image1
    global test_obj_dict

    #run condition
    hosts = res_ops.query_resource(res_ops.HOST)
    if len(hosts) <= 1:
        test_util.test_skip("skip for host_num is not satisfy condition host_num>1")

    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, None, fields=['uuid'])


    image_name1 = 'image1_a'
    image_option = test_util.ImageOption()
    image_option.set_format('qcow2')
    image_option.set_name(image_name1)
    # image_option.set_system_tags('qemuga')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url(os.environ.get('imageUrl_s'))
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(3600 * 1000)

    image1 = zstack_image_header.ZstackTestImage()
    image1.set_creation_option(image_option)
    image1.add_root_volume_template()
    image1.check()
    test_obj_dict.add_image(image1)

    image_name = os.environ.get('imageName_net')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm1 = test_stub.create_vm(image_name1, image_name, l3_name)
    test_obj_dict.add_vm(vm1)

    #create data volume
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name('volume1')
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume.attach(vm1)
    volume.detach()
    # dvol ops test
    test_stub.dvol_ops_test(volume.volume, vm1, "DVOL_TEST_ALL")
    volume.attach(vm1)

    #create data volume from template
    image_option2 = test_util.ImageOption()
    image_option2.set_data_volume_uuid(volume.volume.uuid)
    image_option2.set_name('data_template')
    image_option2.set_backup_storage_uuid_list([bss[0].uuid])
    vol_image = img_ops.create_data_volume_template(image_option2)
    #export vol template
    if bss[0].type in [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE]:
        img_ops.export_image_from_backup_storage(vol_image.uuid, bss[0].uuid)
    target_host = test_lib.lib_find_host_by_vm(vm1.vm)
    volume2 = vol_ops.create_volume_from_template(vol_image.uuid, volume.volume.primaryStorageUuid, host_uuid = target_host.uuid)

    #del data volume template
    img_ops.delete_image(vol_image.uuid)

    # dvol ops test
    test_stub.dvol_ops_test(volume2, vm1, "DVOL_TEST_ALL")

    #expunge data volume template
    img_ops.expunge_image(vol_image.uuid)

    # dvol ops test
    test_stub.dvol_ops_test(volume2, vm1, "DVOL_TEST_ALL")

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('deleting and expunge vol image check vol ops Success')

# Will be called only if exception happens in test().
def error_cleanup():
    global image1
    global test_obj_dict

    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        image1.delete()
    except:
        pass

