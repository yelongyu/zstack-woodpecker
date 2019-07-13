# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    if os.getenv('ZSTACK_SIMULATOR') == "yes":
        test_util.test_skip("Simulator env don't support to check about page")
    global mini
    mini = test_stub.MINI()
    mini.check_about_page()
    mini.check_browser_console_log()
    test_util.test_pass('Test Check About Page Successful')


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
