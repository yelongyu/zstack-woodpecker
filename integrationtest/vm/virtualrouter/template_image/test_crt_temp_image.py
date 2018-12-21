'''

Test Create Image Template from Root Volume for VR Vlan test 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time

test_stub = test_lib.lib_get_test_stub()
#test_obj_dict is to track test resource. They will be cleanup if there will be any exception in testing.
test_obj_dict = test_state.TestStateDict()
origin_interval = None
bs_type = None

def test():
    global origin_interval
    global bs_type

    test_util.test_dsc('Create test vm and check')
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for i in bs:
        if i.type == 'AliyunEBS':
            test_util.test_skip('Skip test on AliyunEBS')
    vm1 = test_stub.create_vlan_vm()
    #Without this checking, the image (created later) might be not able to get a DHCP IP, when using to create a new vm. 
    vm1.check()
    test_obj_dict.add_vm(vm1)
    vm1.stop()

    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm1.vm)
    image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
    image_creation_option.set_root_volume_uuid(vm1.vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_image_template')
    bs_type = backup_storage_list[0].type
    if bs_type == 'Ceph':
        origin_interval = conf_ops.change_global_config('ceph', 'imageCache.cleanup.interval', '1')

    image = test_image.ZstackTestImage()
    image.set_creation_option(image_creation_option)
    image.create()

    test_obj_dict.add_image(image)
    image.check()

    test_util.test_dsc('Use new created Image to create a VM')
    new_img_uuid = image.image.uuid

    vm_creation_option = vm1.get_creation_option()

    vm_creation_option.set_image_uuid(new_img_uuid)

    vm2 = test_vm.ZstackTestVm()
    vm2.set_creation_option(vm_creation_option)
    vm2.create()
    test_obj_dict.add_vm(vm2)
    vm2.check()
    vm1.start()
    vm1.check()
    
    vm2.destroy()

    vm1.destroy()
    image.delete()
    if bs_type == 'Ceph':
        time.sleep(60)
    image.check()

    if bs_type == 'Ceph':
        conf_ops.change_global_config('ceph', 'imageCache.cleanup.interval', origin_interval)

    test_util.test_pass('Create Image Template Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    global origin_interval
    global bs_type
    if bs_type == 'Ceph':
        conf_ops.change_global_config('ceph', 'imageCache.cleanup.interval', origin_interval)

    test_lib.lib_error_cleanup(test_obj_dict)

