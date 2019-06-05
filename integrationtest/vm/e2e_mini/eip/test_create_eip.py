# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_eip()
    mini.check_browser_console_log()
    test_util.test_pass('Create EIP Successful')

def env_recover():
    global mini
    mini.delete_eip()
    mini.close()

def error_cleanup():
    global mini
    try:
        mini.delete_eip()
        mini.close()
    except:
        pass
