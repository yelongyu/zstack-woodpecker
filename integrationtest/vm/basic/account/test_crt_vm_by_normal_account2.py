'''

New Integration Test for creating KVM VM with volume by normal account

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
    account_pass = hashlib.sha512(account_name).hexdigest()
    test_account = acc_ops.create_normal_account(account_name, account_pass)
    test_account_uuid = test_account.uuid

    test_account_session = acc_ops.login_by_account(account_name, account_pass)
    
    test_stub.share_admin_resource([test_account_uuid])
    vm = test_stub.create_vm_with_volume(session_uuid = test_account_session)
    vm.check()
    volumes_number = len(test_lib.lib_get_all_volumes(vm.vm))
    if volumes_number != 2:
        test_util.test_fail('Did not find 2 volumes for [vm:] %s. But we assigned 1 data volume when create the vm. We only catch %s volumes' % (vm.vm.uuid, volumes_number))
    else:
        test_util.test_logger('Find 2 volumes for [vm:] %s.' % vm.vm.uuid)
    vm.destroy(test_account_session)
    vm.check()
    acc_ops.delete_account(test_account_uuid)
    test_util.test_pass('Create VM with volume by normal user account Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global test_account_uuid
    if vm:
        vm.destroy()
    if test_account_uuid:
        acc_ops.delete_account(test_account_uuid)
