# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
volume_name_list = ['volume-' + test_stub.get_time_postfix() for _ in range(3)]

def test():
    global mini
    mini = test_stub.MINI()
    for volume_name in volume_name_list:
        mini.create_volume(name=volume_name)

    for view in ['card', 'list']:
        mini.delete_volume(volume_name_list, view=view, corner_btn=False)
        mini.resume(volume_name_list, 'volume', view=view)
    mini.check_browser_console_log()
    test_util.test_pass('Batch Delete Resume Volume Test Successful')


def env_recover():
    global mini
    mini.expunge_volume(volume_name_list)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.expunge_volume(volume_name_list)
        mini.close()
    except:
        pass
