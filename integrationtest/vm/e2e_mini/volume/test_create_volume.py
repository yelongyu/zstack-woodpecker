# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import volume

volume_ops = None

def test():
    global volume_ops
    volume_ops = volume.VOLUME()
    volume_ops.create_volume()
    volume_ops.check_browser_console_log()
    test_util.test_pass('Create Volume Successful')


def env_recover():
    global volume_ops
    volume_ops.delete_volume()
    volume_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global volume_ops
    try:
        volume_ops.delete_volume()
        volume_ops.close()
    except:
        pass
