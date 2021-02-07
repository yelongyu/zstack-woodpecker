'''

Test Delete new created image template and make sure all information are deleted.
This is regression test cases for bug #46.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstackwoodpecker.operations.resource_operations as res_ops

test_stub = test_lib.lib_get_test_stub()
#test_obj_dict is to track test resource. They will be cleanup if there will be any exception in testing.
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict

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
    image_creation_option.set_timeout('600000')

    image = test_image.ZstackTestImage()
    image.set_creation_option(image_creation_option)
    image.create()
    test_obj_dict.add_image(image)

    image.delete()
    image.check()

    test_util.test_pass('Delete Image Template Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
