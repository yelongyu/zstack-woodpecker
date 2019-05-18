# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
image_name_list = ['image-' + test_stub.get_time_postfix() for _ in range(3)]

def test():
    global mini
    mini = test_stub.MINI()
    for image_name in image_name_list:
        mini.add_image(name=image_name)
    for view in ['card', 'list']:
        mini.delete_image(image_name_list, view=view, corner_btn=False)
        mini.resume(image_name_list, 'image', view=view)
    mini.check_browser_console_log()
    test_util.test_pass('Batch Delete Resume Images Test Successful')


def env_recover():
    global mini
    mini.delete_image(image_name_list, corner_btn=False)
    mini.expunge_image(image_name_list)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_image(image_name_list, corner_btn=False)
        mini.expunge_image(image_name_list)
        mini.close()
    except:
        pass
