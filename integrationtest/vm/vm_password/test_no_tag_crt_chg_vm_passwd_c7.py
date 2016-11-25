'''
test for changing vm password when imported image has no system tag
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import test_stub


vm = None

root_password_list = ["password",  "95_aaapcn",  "_0aIGFDFBBN", "a1_ab"]

def test():
    global vm
    test_util.test_dsc('create VM with setting password')

    for root_password in root_password_list:
        test_util.test_dsc("root_password: \"%s\"" %(root_password))
        vm = test_stub.create_vm(vm_name = 'c7-vm-no-sys-tag', image_name = "imageName_i_c7_no_tag", root_password=root_password)

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

        if not test_lib.lib_check_login_in_vm(vm.get_vm(), "root", root_password):
            test_util.test_fail("create vm with root password: %s failed", root_password)

        # stop vm && change vm password
        vm.stop()
        inv = vm_ops.change_vm_password(vm.get_vm().uuid, "root", test_stub.original_root_password)
        if not inv:
            test_util.test_fail("recover vm password failed")

        vm.start()
        vm.check()

        vm.destroy()
        vm.check()

        vm.expunge()
        vm.check()

    test_util.test_pass('Set password when VM is creating is successful.')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
        vm.expunge()
