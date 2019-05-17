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

    for view in ['card', 'list']:
        # Delete button
        mini.delete_volume(volume_name, view=view)
        # Resume button
        mini.resume(volume_name, 'volume', view=view)

        # Delete via more operation
        mini.delete_volume(volume_name, view=view, corner_btn=False)
        # Resume by more ops
        mini.resume(volume_name, 'volume', view=view, details_page=True)

        # Delete via more operation in details page
        mini.delete_volume(volume_name, view=view, corner_btn=False, details_page=True)
    mini.check_browser_console_log()
    test_util.test_pass('Delete Resume Volume Test Successful')


def env_recover():
    global mini
    mini.expunge_volume(volume_name)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.expunge_volume(volume_name)
        mini.close()
    except:
        pass
