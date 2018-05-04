'''
Test for deleting and expunge vol template check vol created from template ops.

The key step:
-add iso
-create vm from iso
-create data vol1 from template
-create template2 from data vol1
-create data vol2 from template2
-delete template2
-do data vol all ops test on data vol2
-expunge template2
-do data vol all ops test on data vol2

@author: PxChen
'''

import os
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.image_operations as img_ops

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

    cond = res_ops.gen_query_conditions("status", '=', "Connected")
    ps = res_ops.query_resource_fields(res_ops.PRIMARY_STORAGE, cond, None, fields=['uuid'])
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, cond, None, fields=['uuid'])

    # add iso and create vm from iso
    iso = test_stub.add_test_minimal_iso('minimal_iso')
    test_obj_dict.add_image(iso)
    root_volume_offering = test_stub.add_test_root_volume_offering('root-disk-iso', 10737418240)
    test_obj_dict.add_disk_offering(root_volume_offering)
    vm_offering = test_stub.add_test_vm_offering(2, 1024*1024*1024, 'iso-vm-offering')
    test_obj_dict.add_instance_offering(vm_offering)
    vm = test_stub.create_vm_with_iso_for_test(vm_offering.uuid, iso.image.uuid, root_volume_offering.uuid, 'iso-vm')
    test_obj_dict.add_vm(vm)

    #check vm
    vm_inv = vm.get_vm()
    test_lib.lib_set_vm_host_l2_ip(vm_inv)
    test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, 22, 1800)

    #add data volume template
    template_option = test_util.ImageOption()
    template_option.set_name('data-volume-template')
    template_option.set_backup_storage_uuid_list([bss[0].uuid])
    template_option.set_format('qcow2')
    template_option.set_url('http://192.168.200.100/mirror/diskimages/data_volume_image_chunli_200M-4M.qcow2')
    template_inv = img_ops.add_data_volume_template(template_option)
    template = test_image.ZstackTestImage()
    template.set_image(template_inv)
    template.set_creation_option(template_option)
    test_obj_dict.add_image(template)

    #export vol template
    if bss[0].type in [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE]:
        img_ops.export_image_from_backup_storage(template.image.uuid, bss[0].uuid)
    #create data volume from template
    target_host = test_lib.lib_find_host_by_vm(vm.vm)
    volume = vol_ops.create_volume_from_template(template.image.uuid, ps[0].uuid,
                                                  host_uuid=target_host.uuid)
    # create template from data volume
    template_option2 = test_util.ImageOption()
    template_option2.set_data_volume_uuid(volume.uuid)
    template_option2.set_name('data-template-from-vol')
    template_option2.set_backup_storage_uuid_list([bss[0].uuid])
    template2 = img_ops.create_data_volume_template(template_option2)
    #export vol template
    if bss[0].type in [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE]:
        img_ops.export_image_from_backup_storage(template2.uuid, bss[0].uuid)
    volume2 = vol_ops.create_volume_from_template(template2.uuid, volume.primaryStorageUuid, host_uuid = target_host.uuid)

    #del data volume template
    img_ops.delete_image(template2.uuid)

    # dvol ops test
    test_stub.dvol_ops_test(volume2, vm, "DVOL_TEST_ALL")

    #expunge data volume template
    img_ops.expunge_image(template2.uuid)

    # dvol ops test
    test_stub.dvol_ops_test(volume2, vm, "DVOL_TEST_ALL")

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
