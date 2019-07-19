# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

volume = test_lib.lib_get_specific_stub('e2e_mini/volume', 'volume')

volume_ops = None
volume_name = 'volume-' + volume.get_time_postfix()

def test():
    global volume_ops
    volume_ops = volume.VOLUME()
    volume_ops.create_volume(name=volume_name)

    for view in ['card', 'list']:
        # Delete button
        volume_ops.delete_volume(volume_name, view=view)
        # Resume button
        volume_ops.resume(volume_name, 'volume', view=view)

        # Delete via more operation
        volume_ops.delete_volume(volume_name, view=view, corner_btn=False)
        # Resume by more ops
        volume_ops.resume(volume_name, 'volume', view=view, details_page=True)

        # Delete via more operation in details page
        volume_ops.delete_volume(volume_name, view=view, corner_btn=False, details_page=True)
        # Resume button
        volume_ops.resume(volume_name, 'volume', view=view)
    volume_ops.check_browser_console_log()
    test_util.test_pass('Delete Resume Volume Test Successful')


def env_recover():
    global volume_ops
    volume_ops.expunge_volume(volume_name)
    volume_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global volume_ops
    try:
        volume_ops.expunge_volume(volume_name)
        volume_ops.close()
    except:
        pass
