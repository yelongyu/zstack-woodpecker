# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.add_image()
    # mini.add_image(adding_type='file', local_file='C:\\Users\\Administrator\\Desktop\\centos7-test.qcow2')
    mini.check_browser_console_log()
    test_util.test_pass('Add Image Successful')

def env_recover():
    global mini
    mini.expunge_image()
    mini.close()

def error_cleanup():
    global mini
    try:
        mini.expunge_image()
        mini.close()
    except:
        pass
