# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.add_image()
    test_util.test_pass('Add image Successful')

def env_recover():
    global mini
    mini.close()

def error_cleanup():
    global mini
    try:
        mini.close()
    except:
        pass
