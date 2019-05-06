# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
volume_name = 'test-volume'
volume_new_name='volume-rename'

def test():
    global mini
    global volume_name
    global volume_new_name
    mini = test_stub.MINI()
    mini.create_volume(name=volume_name)
    mini.modify_info(res_type='volume', res_name=volume_name, new_name=volume_new_name, new_dsc='test dsc')
    
    test_util.test_pass('Test volume update info Successful')


def env_recover():
    global mini
    global volume_new_name
    mini.delete_volume(volume_new_name)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_volume()
        mini.close()
    except:
        pass
