'''
New Integration Test for 2 normal accounts zstack-cli login

@author: quarkonics
'''
import hashlib
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_account as test_account
import zstacklib.utils.shell as shell

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def login_cli_by_account(account_name, account_pass):
    cmd = '''zstack-cli << EOF
LogInByAccount accountName=%s password=%s
quit
''' % (account_name, account_pass)
    return shell.call(cmd)

def logout_cli():
    cmd = '''zstack-cli << EOF
LogOut
quit
'''
    return shell.call(cmd)

def test():
    import uuid
    login_output = login_cli_by_account('admin', 'password')
    if login_output.find('%s >>>' % ('admin')) < 0:
        test_util.test_fail('zstack-cli is not display correct name for logined account: %s' % (login_output))

    account_name1 = uuid.uuid1().get_hex()
    account_pass1 = hashlib.sha512(account_name1).hexdigest()
    test_account1 = test_account.ZstackTestAccount()
    test_account1.create(account_name1, account_pass1)
    test_obj_dict.add_account(test_account1)
    login_output = login_cli_by_account(account_name1, account_name1)
    if login_output.find('%s >>>' % (account_name1)) < 0:
        test_util.test_fail('zstack-cli is not display correct name for logined account: %s' % (login_output))
    
    account_name2 = uuid.uuid1().get_hex()
    account_pass2 = hashlib.sha512(account_name2).hexdigest()
    test_account2 = test_account.ZstackTestAccount()
    test_account2.create(account_name2, account_pass2)
    test_obj_dict.add_account(test_account2)
    test_account_uuid2 = test_account2.get_account().uuid
    login_output = login_cli_by_account(account_name2, account_name2)
    if login_output.find('%s >>>' % (account_name2)) < 0:
        test_util.test_fail('zstack-cli is not display correct name for logined account %s' % (login_output))

    logout_output = logout_cli()
    if logout_output.find('- >>>') < 0:
        test_util.test_fail('zstack-cli is not display correct after logout: %s' % (login_output))

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
