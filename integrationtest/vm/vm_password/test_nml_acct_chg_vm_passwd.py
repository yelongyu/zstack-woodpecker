'''
New Integration Test for changing password by normal account
@author: SyZhao
'''

import apibinding.inventory as inventory
import hashlib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstacklib.utils.ssh as ssh
import test_stub



lib_test_stub = test_lib.lib_get_test_stub()

vm = None
test_account_uuid = None
test_account_session = None

users   = ["root",      "root",       "_a",          "aa"  ]
passwds = ["password",  "95_aaapcn",  "_0aIGFDFBBN", "a1_" ]

exist_users = ["root"]

def test():
    global vm, test_account_uuid, test_account_session
    import uuid
    account_name = uuid.uuid1().get_hex()
    account_pass = uuid.uuid1().get_hex()
    account_pass = hashlib.sha512(account_name).hexdigest()
    test_account = acc_ops.create_normal_account(account_name, account_pass)
    test_account_uuid = test_account.uuid
    test_account_session = acc_ops.login_by_account(account_name, account_pass)
    test_stub.share_admin_resource([test_account_uuid])

    vm = test_stub.create_vm(vm_name = 'c7-vm', image_name = "imageName_i_c7", session_uuid = test_account_session)
    vm.check()

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

    for (usr,passwd) in zip(users, passwds):
        if usr not in exist_users:
            test_stub.create_user_in_vm(vm.get_vm(), usr, passwd)
            exist_users.append(usr)

        #When vm is running:
        inv = vm_ops.change_vm_password(vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = test_account_session)
        if not inv:
            test_util.test_fail("change vm password failed")

        if not test_lib.lib_check_login_in_vm(vm.get_vm(), usr, passwd):
            test_util.test_fail("create vm with user:%s password: %s failed", usr, passwd)

        #When vm is stopped:
        vm.stop(session_uuid = test_account_session)
        inv = vm_ops.change_vm_password(vm.get_vm().uuid, "root", test_stub.original_root_password, session_uuid = test_account_session)
        if not inv:
            test_util.test_fail("recover vm password failed")

        vm.start(session_uuid = test_account_session)
        vm.check()

    vm.destroy(test_account_session)
    vm.check()
    vm.expunge(test_account_session)
    vm.check()
    acc_ops.delete_account(test_account_uuid)
    test_util.test_pass('change vm password by normal user account Success')


#Will be called only if exception happens in test().
def error_cleanup():
    global vm, test_account_uuid, test_account_session
    if vm:
        vm.destroy(test_account_session)
    if test_account_uuid:
        acc_ops.delete_account(test_account_uuid)
