# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.change_mini_password(password='123456')
    mini.logout()
    mini.login(password='123456')
    mini.change_mini_password(password='password')
    mini.logout()
    mini.login()
    mini.check_browser_console_log()
    test_util.test_pass('Test Change MINI Password Successful')


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
