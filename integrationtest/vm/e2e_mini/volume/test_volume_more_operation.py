# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
volume_new_name='volume-rename'

def test():
    global mini
    global volume_new_name
    mini = test_stub.MINI()
    mini.create_vm()
    mini.create_volume()
    mini.attach_volume()
    mini.detach_volume()
    mini.modify_volume_info(new_name=volume_new_name, new_dsc='test dsc')
    
    test_util.test_pass('Test volume moreOparation Successful')


def env_recover():
    global mini
    global volume_new_name
    mini.delete_vm()
    mini.delete_volume(volume_new_name)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_vm()
        mini.delete_volume()
        mini.close()
    except:
        pass
