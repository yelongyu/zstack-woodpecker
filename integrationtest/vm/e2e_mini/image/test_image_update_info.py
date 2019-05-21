# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
image_name = 'test-image'
image_new_name='image-rename'

def test():
    global mini
    global image_name
    global image_new_name
    mini = test_stub.MINI()
    mini.add_image(name=image_name)
    mini.update_info(res_type='image', res_name=image_name, new_name=image_new_name, new_dsc='test dsc')
    mini.check_browser_console_log()
    test_util.test_pass('Test Image Update Info Successful')


def env_recover():
    global mini
    global image_new_name
    mini.delete_image(image_new_name)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_image()
        mini.close()
    except:
        pass
