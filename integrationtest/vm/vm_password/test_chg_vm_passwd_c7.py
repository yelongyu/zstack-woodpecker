'''
Change VM password
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstacklib.utils.ssh as ssh
import test_stub


exist_users = ["root"]

users   = ["root",      "root",       "_a",          "aa"  ]
passwds = ["password",  "95_aaapcn",  "_0aIGFDFBBN", "a1_" ]


vm = None

def test():
    global vm, exist_users
    test_util.test_dsc('change VM with assigned password test')

    vm = test_stub.create_vm(vm_name = 'check-change-password-vm', image_name = "imageName_i_c7")
    vm.check()

    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    for bs in backup_storage_list:
        if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            break
        if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
            break
    else:
        vm.destroy()
        test_util.test_skip('Not find image store type backup storage.')

    for (usr,passwd) in zip(users, passwds):
        if usr not in exist_users:
            test_stub.create_user_in_vm(vm.get_vm(), usr, passwd) 
            exist_users.append(usr)

        #When vm is running:
        inv = vm_ops.change_vm_password(vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None)
        if not inv:
            test_util.test_fail("change vm password failed")

        if not test_lib.lib_check_login_in_vm(vm.get_vm(), usr, passwd):
            test_util.test_fail("create vm with user:%s password: %s failed", usr, passwd)
        
        #When vm is stopped:
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
