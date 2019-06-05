# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
volume_name = 'volume-' + test_stub.get_time_postfix()

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_volume(name=volume_name)
    mini.upgrade_capacity(volume_name, 'volume', '5 GB')
    mini.check_browser_console_log()
    test_util.test_pass('Test Upgrade Volume Capacity Successful')


def env_recover():
    global mini
    global volume_name
    mini.delete_volume(volume_name)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_volume()
        mini.close()
    except:
        pass
