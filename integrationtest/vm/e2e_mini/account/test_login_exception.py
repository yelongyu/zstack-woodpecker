# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.logout()

    mini.login_without_account_or_password(with_account=False, with_password=False)
    mini.refresh_page()
    mini.login_without_account_or_password(with_account=True, with_password=False)
    mini.refresh_page()
    mini.login_without_account_or_password(with_account=False, with_password=True)
    mini.refresh_page()

    mini.login_with_wrong_account_or_password(wrong_account=True, wrong_password=True)
    mini.refresh_page()
    mini.login_with_wrong_account_or_password(wrong_account=True, wrong_password=False)
    mini.refresh_page()
    mini.login_with_wrong_account_or_password(wrong_account=False, wrong_password=True)
    mini.refresh_page()

    mini.check_browser_console_log()
    test_util.test_pass('Test Login Exception Successful')


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
