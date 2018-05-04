'''
Test for deleting and expunge image cloned vm ops.

The key step:
-add image1
-create vm1 from image1
-export image1
-clone vm2 from vm1
-del image1
-create snapshot from vm2
-expunge image1
-resize data volume on vm2

@author: PxChen
'''

import os
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
image1 = None

def test():
    global image1
    global test_obj_dict

    #run condition
    allow_bs_list = [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE, inventory.CEPH_BACKUP_STORAGE_TYPE]
    test_lib.skip_test_when_bs_type_not_in_list(allow_bs_list)

    hosts = res_ops.query_resource(res_ops.HOST)
    if len(hosts) <= 1:
        test_util.test_skip("skip for host_num is not satisfy condition host_num>1")
    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, None, fields=['uuid'])

    image_name1 = 'image1_a'
    image_option = test_util.ImageOption()
    image_option.set_format('qcow2')
    image_option.set_name(image_name1)
    #image_option.set_system_tags('qemuga')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url(os.environ.get('imageUrl_s'))
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(3600*1000)

    image1 = zstack_image_header.ZstackTestImage()
    image1.set_creation_option(image_option)
    image1.add_root_volume_template()
    image1.check()

    #export image
    if bss[0].type in [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE]:
        image1.export()

    image_name = os.environ.get('imageName_net')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm = test_stub.create_vm('test-vm', image_name, l3_name)
    test_obj_dict.add_vm(vm)

    # clone vm
    cloned_vm_name = ['cloned_vm']
    cloned_vm_obj = vm.clone(cloned_vm_name)[0]
    test_obj_dict.add_vm(cloned_vm_obj)

    # delete image
    image1.delete()

    # vm ops test
    test_stub.vm_ops_test(cloned_vm_obj, "VM_TEST_SNAPSHOT")

    # expunge image
    image1.expunge()

    # vm ops test
    test_stub.vm_ops_test(cloned_vm_obj, "VM_TEST_RESIZE_DVOL")

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Cloned VM ops for BS Success')

# Will be called only if exception happens in test().
def error_cleanup():
    global image1
    global test_obj_dict

    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        image1.delete()
    except:
        pass
