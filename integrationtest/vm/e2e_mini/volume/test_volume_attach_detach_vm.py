# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_vm()
    mini.create_volume()
    mini.attach_volume()
    mini.detach_volume()
    
    test_util.test_pass('Test volume to attach vm and detach vm Successful')


def env_recover():
    global mini
    mini.delete_vm()
    mini.delete_volume()
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_vm()
        mini.delete_volume()
        mini.close()
    except:
        pass
