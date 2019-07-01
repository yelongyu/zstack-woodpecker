# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import volume

volume_ops = None
volume_name_list = ['volume-' + volume.get_time_postfix() for _ in range(3)]

def test():
    global volume_ops
    volume_ops = volume.VOLUME()
    for volume_name in volume_name_list:
        volume_ops.create_volume(name=volume_name)

    for view in ['card', 'list']:
        volume_ops.delete_volume(volume_name_list, view=view, corner_btn=False)
        volume_ops.resume(volume_name_list, 'volume', view=view)
    volume_ops.check_browser_console_log()
    test_util.test_pass('Batch Delete Resume Volumes Test Successful')


def env_recover():
    global volume_ops
    volume_ops.expunge_volume(volume_name_list)
    volume_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global volume_ops
    try:
        volume_ops.expunge_volume(volume_name_list)
        volume_ops.close()
    except:
        pass
