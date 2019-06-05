# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_network()
    mini.check_browser_console_log()
    test_util.test_pass('Create network Successful')

def env_recover():
    global mini
    mini.delete_network()
    mini.close()

def error_cleanup():
    global mini
    try:
        mini.delete_network()
        mini.close()
    except:
        pass
