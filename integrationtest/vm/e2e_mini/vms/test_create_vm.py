# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_vm(provisioning=u'厚置备', view='list')
    mini.create_vm(provisioning=u'精简置备')
    mini.check_browser_console_log()
    test_util.test_pass('Create VM Successful')


def env_recover():
    global mini
    mini.expunge_vm()
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.expunge_vm()
        mini.close()
    except:
        pass
