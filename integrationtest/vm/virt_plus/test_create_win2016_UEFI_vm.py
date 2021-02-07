'''

New Integration test for testing create a vm with UEFI BIOS.

@author: Pengtao.Zhang
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import subprocess
import time
import os
import uuid

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    os.system('swapon -a')
    instance_offering_name = os.environ.get('instanceOfferingName_m')
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid
    img_option = test_util.ImageOption()
    UEFI_image_url = os.environ.get('imageUrl_win2016_UEFI')
    image_name = os.environ.get('imageName_win2016_UEFI')
    img_option.set_name(image_name)
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_format('qcow2')
    img_option.set_url(UEFI_image_url)
    img_option.set_timeout(6000000)
    img_option.set_system_tags("bootMode::UEFI")
    image_inv = img_ops.add_root_volume_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    test_obj_dict.add_image(image)
    vm = test_stub.create_vm(image_name = os.environ.get('imageName_win2016_UEFI'), instance_offering_uuid = instance_offering_uuid)
    test_obj_dict.add_vm(vm)
    time.sleep(120)
    vm.check()
    vm_ip = vm.get_vm().vmNics[0].ip
    retcode = subprocess.call(["ping", "-c","4",vm_ip])
    if retcode != 0:
        test_util.test_fail('Create VM Test win2016 UEFI failed.')
    else:
        test_util.test_pass('Create VM Test win2016 UEFI Success.')


    vm.destroy()
    test_util.test_pass('Create VM Test win2016 UEFI Success')

    #Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
