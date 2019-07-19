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
    volume_ops.upgrade_capacity(volume_name, 'volume', '5 GB')
    volume_ops.check_browser_console_log()
    test_util.test_pass('Test Upgrade Volume Capacity Successful')


def env_recover():
    global volume_ops
    global volume_name
    volume_ops.delete_volume(volume_name)
    volume_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global volume_ops
    try:
        volume_ops.delete_volume()
        volume_ops.close()
    except:
        pass
