# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    time = 9
    mini = test_stub.MINI()
    mini.logout()
    while time > 0:
        mini.login()
        mini.logout()
        time -= 1
    test_util.test_pass('Test login and logout Successful')


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
