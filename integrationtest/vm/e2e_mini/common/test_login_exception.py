# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.logout()

    mini.login_without_accountname_or_password(with_accountName=False, with_password=False)
    mini.refresh_page()
    mini.login_without_accountname_or_password(with_accountName=True, with_password=False)
    mini.refresh_page()
    mini.login_without_accountname_or_password(with_accountName=False, with_password=True)
    mini.refresh_page()

    mini.login_with_wrong_accountname_or_password(waccountName=True, wpassword=True)
    mini.refresh_page()
    mini.login_with_wrong_accountname_or_password(waccountName=True, wpassword=False)
    mini.refresh_page()
    mini.login_with_wrong_accountname_or_password(waccountName=False, wpassword=True)
    mini.refresh_page()

    test_util.test_pass('Test login exception Successful')


def env_recover():
    global mini
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.close()
    except:
        pass
