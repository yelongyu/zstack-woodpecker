# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import image

image_ops = None
image_name = 'test-image'
image_new_name='image-rename'

def test():
    global image_ops
    global image_name
    global image_new_name
    image_ops = image.IMAGE()
    image_ops.add_image(name=image_name)
    image_ops.update_info(res_type='image', res_name=image_name, new_name=image_new_name, new_dsc='test dsc')
    image_ops.check_browser_console_log()
    test_util.test_pass('Test Image Update Info Successful')


def env_recover():
    global image_ops
    global image_new_name
    image_ops.delete_image(image_new_name)
    image_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global image_ops
    try:
        image_ops.delete_image()
        image_ops.close()
    except:
        pass
