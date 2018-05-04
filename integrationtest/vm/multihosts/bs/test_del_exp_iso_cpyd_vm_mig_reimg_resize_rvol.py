'''
Test for deleting and expunge iso created vm ops.

The key step:
-add iso
-create vm1 from iso
-create image from vm1
-del expunge and detach iso
-export image
-create vm2 from image
-migrate vm2
-del image
-reimage vm2
-expunge image
-resize vm2 root volume

@author: PxChen
'''

import os
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.image_operations as img_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
image = None

def test():
    global image
    global test_obj_dict

    # run condition
    hosts = res_ops.query_resource(res_ops.HOST)
    if len(hosts) <= 1:
        test_util.test_skip("skip for host_num is not satisfy condition host_num>1")

    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, None, fields=['uuid'])

    # add iso and create vm from iso
    iso = test_stub.add_test_minimal_iso('minimal_iso')
    test_obj_dict.add_image(iso)
    root_volume_offering = test_stub.add_test_root_volume_offering('root-disk-iso', 10737418240)
    test_obj_dict.add_disk_offering(root_volume_offering)
    vm_offering = test_stub.add_test_vm_offering(2, 1024*1024*1024, 'iso-vm-offering')
    test_obj_dict.add_instance_offering(vm_offering)
    vm = test_stub.create_vm_with_iso_for_test(vm_offering.uuid, iso.image.uuid, root_volume_offering.uuid, 'iso-vm')
    test_obj_dict.add_vm(vm)

    # check vm
    vm_inv = vm.get_vm()
    test_lib.lib_set_vm_host_l2_ip(vm_inv)
    test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, 22, 1800)

    #create image by vm root volume
    created_vm_img_name = "created_vm_image1"
    img_option = test_util.ImageOption()
    img_option.set_backup_storage_uuid_list([bss[0].uuid])
    img_option.set_root_volume_uuid(vm.vm.rootVolumeUuid)
    img_option.set_name(created_vm_img_name)
    image = test_image.ZstackTestImage()
    image.set_creation_option(img_option)
    image.create()
    test_obj_dict.add_image(image)

    #export image
    if bss[0].type in [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE]:
        image.export()

    #create vm
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm2 = test_stub.create_vm('image-vm', created_vm_img_name, l3_name)

    #del expunge and detach iso
    iso.delete()
    iso.expunge()
    img_ops.detach_iso(vm.vm.uuid)
    # vm ops test
    test_stub.vm_ops_test(vm2, "VM_TEST_MIGRATE")

    # del and expunge image2
    image.delete()
    # vm ops test
    test_stub.vm_ops_test(vm2, "VM_TEST_REIMAGE")
    image.expunge()
    # vm ops test
    test_stub.vm_ops_test(vm2, "VM_TEST_RESIZE_RVOL")

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Cloned VM ops for BS Success')

# Will be called only if exception happens in test().
def error_cleanup():
    global image
    global test_obj_dict

    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        image.delete()
    except:
        pass