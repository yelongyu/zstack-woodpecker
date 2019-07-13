# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import volume

volume_ops = None
volume_name = 'test-volume'
volume_new_name='volume-rename'

def test():
    global volume_ops
    global volume_name
    global volume_new_name
    volume_ops = volume.VOLUME()
    volume_ops.create_volume(name=volume_name)
    volume_ops.update_info(res_type='volume', res_name=volume_name, new_name=volume_new_name, new_dsc='test dsc')
    volume_ops.check_browser_console_log()
    test_util.test_pass('Test Volume Update Info Successful')


def env_recover():
    global volume_ops
    global volume_new_name
    volume_ops.delete_volume(volume_new_name)
    volume_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global volume_ops
    try:
        volume_ops.delete_volume()
        volume_ops.close()
    except:
        pass
