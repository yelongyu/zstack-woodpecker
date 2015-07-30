'''
New Integration Test for all kinds of VM operations by normal account

@author: Youyk
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
vm = None
test_account_uuid = None

def test():
    global vm
    global test_account_uuid
    import uuid
    account_name = uuid.uuid1().get_hex()
    account_pass = uuid.uuid1().get_hex()
    test_account = acc_ops.create_normal_account(account_name, account_name)
    test_account_uuid = test_account.uuid

    test_account_session = acc_ops.login_by_account(account_name, account_name)
    
    test_stub.share_admin_resource([test_account_uuid])
    vm = test_stub.create_vm(session_uuid = test_account_session)
    vm.check()
    vm.stop(session_uuid = test_account_session)
    vm.check()
    vm.start(session_uuid = test_account_session)
    vm.check()
    vm.reboot(session_uuid = test_account_session)
    vm.check()
    vm.destroy(test_account_session)
    vm.check()
    acc_ops.delete_account(test_account_uuid)
    test_util.test_pass('Operate VM by normal user account Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global test_account_uuid
    if vm:
        vm.destroy()
    if test_account_uuid:
        acc_ops.delete_account(test_account_uuid)
