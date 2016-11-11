'''
New Integration Test for 2 normal users zstack-cli login

@author: MengLai
'''
import hashlib
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_account as test_account
import zstackwoodpecker.zstack_test.zstack_test_user as test_user
import zstacklib.utils.shell as shell

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def login_cli_by_user(account_name, user_name, user_pass):
    cmd = '''zstack-cli << EOF
LogInByUser accountName=%s userName=%s password=%s
quit
''' % (account_name, user_name, user_pass)
    return shell.call(cmd)

def test_query():
    cmd = '''zstack-cli << EOF
QueryVmNic
quit
'''
    return shell.call(cmd)

def logout_cli():
    cmd = '''zstack-cli << EOF
LogOut
quit
'''
    return shell.call(cmd)

def test():
    import uuid
    
    test_util.test_dsc('Create an normal account and login with it')
    account_name1 = uuid.uuid1().get_hex()
    account_pass1 = hashlib.sha512(account_name1).hexdigest()
    test_account1 = test_account.ZstackTestAccount()
    test_account1.create(account_name1, account_pass1)
    test_obj_dict.add_account(test_account1)
    test_account_session = acc_ops.login_by_account(account_name1, account_pass1)

    test_util.test_dsc('Create an normal user-1 under the new account and login with it')
    user_name1 = uuid.uuid1().get_hex()
    user_pass1 = hashlib.sha512(user_name1).hexdigest()
    test_user1 = test_user.ZstackTestUser() 
    test_user1.create(user_name1, user_pass1, session_uuid = test_account_session)
    test_obj_dict.add_user(test_user1)
    login_output = login_cli_by_user(account_name1, user_name1, user_name1) 
    if login_output.find('%s/%s >>>' % (account_name1, user_name1)) < 0:
        test_util.test_fail('zstack-cli is not display correct name for logined user: %s' % (login_output))

    test_util.test_dsc('Create an normal user-2 under the new account and login with it')
    user_name2 = uuid.uuid1().get_hex()
    user_pass2 = hashlib.sha512(user_name2).hexdigest()
    test_user2 = test_user.ZstackTestUser()
    test_user2.create(user_name2, user_pass2, session_uuid = test_account_session)
    test_obj_dict.add_user(test_user2)
    login_output = login_cli_by_user(account_name1, user_name2, user_name2)
    if login_output.find('%s/%s >>>' % (account_name1, user_name2)) < 0:
        test_util.test_fail('zstack-cli is not display correct name for logined user: %s' % (login_output))

    test_util.test_dsc('Delete user-2 and check the login status')
    test_user2.delete()
    test_obj_dict.rm_user(test_user2)
    query_output = test_query()
    if query_output.find('- >>>') < 0:
        test_util.test_fail('zstack-cli is not display correct after delete user: %s' % (query_output))

    test_util.test_dsc('login user-1, logout user-1 and check the login status')
    login_output = login_cli_by_user(account_name1, user_name1, user_name1)
    if login_output.find('%s/%s >>>' % (account_name1, user_name1)) < 0:
        test_util.test_fail('zstack-cli is not display correct name for logined user: %s' % (login_output))
    logout_output = logout_cli()
    if logout_output.find('- >>>') < 0:
        test_util.test_fail('zstack-cli is not display correct after logout: %s' % (login_output))

    test_user1.delete()
    test_account1.delete()
    test_obj_dict.rm_user(test_user1)
    test_obj_dict.rm_account(test_account1)

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
