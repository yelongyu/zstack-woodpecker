'''
New Integration Test for 2 normal accounts to operate VM 

@author: Youyk
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.header.vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_account as test_account

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    import uuid
    account_name1 = uuid.uuid1().get_hex()
    account_pass1 = uuid.uuid1().get_hex()
    test_account1 = test_account.ZstackTestAccount()
    test_account1.create(account_name1, account_pass1)
    test_obj_dict.add_account(test_account1)
    test_account_uuid1 = test_account1.get_account().uuid
    test_account_session1 = acc_ops.login_by_account(account_name1, account_pass1)
    
    account_name2 = uuid.uuid1().get_hex()
    account_pass2 = uuid.uuid1().get_hex()
    test_account2 = test_account.ZstackTestAccount()
    test_account2.create(account_name2, account_pass2)
    test_obj_dict.add_account(test_account2)
    test_account_uuid2 = test_account2.get_account().uuid
    test_account_session2 = acc_ops.login_by_account(account_name2, account_pass2)
    
    test_stub.share_admin_resource([test_account_uuid1, test_account_uuid2])
    vm1 = test_stub.create_user_vlan_vm(session_uuid = test_account_session1)
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm1.stop(session_uuid = test_account_session1)
    vm1.check()

    vm2 = test_stub.create_user_vlan_vm(session_uuid = test_account_session2)
    test_obj_dict.add_vm(vm2)
    vm2.check()

    vm1.start(session_uuid = test_account_session1)
    vm1.check()
    test_account1.delete()
    test_obj_dict.rm_account(test_account1)
    vm1.set_state(test_vm_header.DESTROYED)
    vm1.check()
    vr_vm = test_lib.lib_find_vr_by_vm(vm2.get_vm())
    if not vr_vm:
        test_util.test_fail('VR is deleted, after account1 is deleted')

    vm2.check()
    vm2.stop(test_account_session2)
    vm2.start(test_account_session2)
    vm2.check()
    vm2.destroy(test_account_session2)
    test_obj_dict.rm_vm(vm2)

    account_name3 = uuid.uuid1().get_hex()
    account_pass3 = uuid.uuid1().get_hex()
    test_account3 = test_account.ZstackTestAccount()
    test_account3.create(account_name3, account_pass3)
    test_obj_dict.add_account(test_account3)
    test_account_uuid3 = test_account3.get_account().uuid
    test_account_session3 = acc_ops.login_by_account(account_name3, account_pass3)
    test_stub.share_admin_resource([test_account_uuid3])
    vm3 = test_stub.create_user_vlan_vm(session_uuid = test_account_session3)
    test_obj_dict.add_vm(vm3)
    vm3.check()

    vm3.destroy()
    test_obj_dict.rm_vm(vm3)

    test_account3.delete()
    test_obj_dict.rm_account(test_account3)

    test_account2.delete()
    test_obj_dict.rm_account(test_account2)
    test_util.test_pass('Multiple normal account with VM operations test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
