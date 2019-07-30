'''
test for changing vm password when imported image with no system tag add system tag
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import os

test_stub = test_lib.lib_get_specific_stub()


vm = None
vm2 = None
image_uuid = None


root_password_list = ["ab_0123"]

def test():
    global vm, vm2, image_uuid
    test_util.test_dsc('create VM with setting password')

    image_name = "imageName_i_c7_no_tag"
    ps_type = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].type
    if ps_type == 'MiniStorage':
        image_name = os.environ.get(image_name)

    for root_password in root_password_list:
        test_util.test_dsc("root_password: \"%s\"" %(root_password))
        vm = test_stub.create_vm(vm_name='c7-vm-no-sys-tag', image_name=image_name)

        backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
        for bs in backup_storage_list:
            if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
                break
            if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
                break
            if bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
                break
        else:
            vm.destroy()
            test_util.test_skip('Not find image store type backup storage.')

        vm.check()

        #add tag to vm
        tag_ops.create_system_tag('VmInstanceVO', vm.get_vm().uuid, "qemuga")

        vm_ops.set_vm_qga_enable(vm.get_vm().uuid)
        vm_ops.change_vm_password(vm.get_vm().uuid, "root", root_password)

        #create image by the vm with tag
        vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
        root_volume_uuid = vm_root_volume_inv.uuid

        image_option1 = test_util.ImageOption()
        image_option1.set_root_volume_uuid(root_volume_uuid)
        image_option1.set_name('add_tag_vm_to_image')
        image_option1.set_format('qcow2')
        image_option1.set_backup_storage_uuid_list([bs.uuid])

        vm.stop()
        image = img_ops.create_root_volume_template(image_option1)

        #create vm by new image
        vm2 = test_stub.create_vm(vm_name='c7-vm-add-tag-from-previous-vm', image_name="add_tag_vm_to_image")
        if not test_lib.lib_check_login_in_vm(vm2.get_vm(), "root", root_password):
            test_util.test_fail("create vm with user:%s password: %s failed", "root", root_password)

        vm_ops.set_vm_qga_enable(vm2.get_vm().uuid)
        vm_ops.change_vm_password(vm2.get_vm().uuid, "root", root_password)

        image_uuid = image.uuid
        if not image_uuid:
            img_ops.delete_image(image_uuid)
            img_ops.expunge_image(image_uuid)

    test_util.test_pass('add system tag on a no system tag image test passed')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm, vm2, image_uuid
    if not image_uuid:
        img_ops.delete_image(image_uuid)
        img_ops.expunge_image(image_uuid)
    if vm:
        vm.destroy()
        vm.expunge()
