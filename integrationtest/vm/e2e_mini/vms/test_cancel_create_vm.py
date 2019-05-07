# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.cancel_create_operation(res_type='vm', close=False)
    mini.cancel_create_operation(res_type='vm', close=True)
    test_util.test_pass('Create VM Successful')


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
