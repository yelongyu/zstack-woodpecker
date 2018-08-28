'''

New Integration test for testing running vm migration between hosts when attach ISO.

@author: Chenyuan.xu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.test_state as test_state
import apibinding.inventory as inventory
import zstacklib.utils.ssh as ssh
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def exec_cmd_in_vm(vm, cmd, fail_msg):
    ret, output, stderr = ssh.execute(cmd, vm.get_vm().vmNics[0].ip, "root", "password", False, 22)
    if ret != 0:
        test_util.test_fail(fail_msg)

def test():
    global vm
    vm = test_stub.create_vr_vm('migrate_vm', 'imageName_net', 'l3VlanNetwork2')
    vm.check()

    vm_inv = vm.get_vm()
    vm_uuid = vm_inv.uuid


    test_util.test_dsc('Add ISO Image')
    #cond = res_ops.gen_query_conditions('name', '=', 'sftp')
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid


    img_option = test_util.ImageOption()
    img_option.set_name('iso')
    img_option.set_backup_storage_uuid_list([bs_uuid])
    testIsoUrl = os.environ.get('testIsoUrl')
    img_option.set_url(testIsoUrl)
    image_inv = img_ops.add_iso_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
   
    test_obj_dict.add_image(image)

    test_util.test_dsc('Attach ISO to VM')
    cond = res_ops.gen_query_conditions('name', '=', 'iso')
    iso_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    img_ops.attach_iso(iso_uuid, vm_uuid)
    
    time.sleep(10)
    cmd = "mount /dev/sr0 /mnt"
    exec_cmd_in_vm(vm, cmd, "Failed to mount /dev/sr0 /mnt.")

    test_util.test_dsc('Migrate VM')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()

    cmd = "umount /mnt"
    exec_cmd_in_vm(vm, cmd, "Failed to umount /mnt.")

    img_ops.detach_iso(vm_uuid)
    img_ops.attach_iso(iso_uuid, vm_uuid)

    time.sleep(10)
    cmd = "mount /dev/sr0 /mnt"
    exec_cmd_in_vm(vm, cmd, "Failed to mount /dev/sr0 /mnt.")

    cmd = "cat /mnt/Licenses.txt"
    exec_cmd_in_vm(vm, cmd, "Licenses.txt doesn't exist.")

    img_ops.detach_iso(vm_uuid)
    image.delete()
    image.expunge()
    test_obj_dict.rm_image(image)
    vm.destroy()
    test_util.test_pass('Migrate VM Test Success When Attach ISO')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
