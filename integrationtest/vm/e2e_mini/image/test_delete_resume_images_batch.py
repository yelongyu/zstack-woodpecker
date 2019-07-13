# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import image

image_ops = None
image_name_list = ['image-' + image.get_time_postfix() for _ in range(3)]

def test():
    global image_ops
    image_ops = image.IMAGE()
    for image_name in image_name_list:
        image_ops.add_image(name=image_name)
    for view in ['card', 'list']:
        image_ops.delete_image(image_name_list, view=view, corner_btn=False)
        image_ops.resume(image_name_list, 'image', view=view)
    image_ops.check_browser_console_log()
    test_util.test_pass('Batch Delete Resume Images Test Successful')


def env_recover():
    global image_ops
    image_ops.delete_image(image_name_list, corner_btn=False)
    image_ops.expunge_image(image_name_list)
    image_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global image_ops
    try:
        image_ops.delete_image(image_name_list, corner_btn=False)
        image_ops.expunge_image(image_name_list)
        image_ops.close()
    except:
        pass
