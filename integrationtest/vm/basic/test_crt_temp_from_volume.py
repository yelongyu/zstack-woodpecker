'''

Test Create Image Template from Root Volume

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm

test_stub = test_lib.lib_get_specific_stub()

#test_obj_dict is to track test resource. They will be cleanup if there will be any exception in testing.
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict

    test_util.test_dsc('Create test vm and check')
    vm1 = test_stub.create_vm()
    test_obj_dict.add_vm(vm1)
    vm1.stop()

    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm1.vm)
    image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
    image_creation_option.set_root_volume_uuid(vm1.vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_image_template')

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
    image.check()

    test_util.test_pass('Create Image Template Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

