# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

image = test_lib.lib_get_specific_stub('e2e_mini/image', 'image')

image_ops = None
image_name = 'image-' + image.get_time_postfix()

def test():
    global image_ops
    image_ops = image.IMAGE()
    image_ops.add_image(name=image_name)

    for view in ['card', 'list']:
        # Delete button
        image_ops.delete_image(image_name, view=view)
        # Resume button
        image_ops.resume(image_name, 'image', view=view)

        # Delete via more operation
        image_ops.delete_image(image_name, view=view, corner_btn=False)
        # Resume by more ops
        image_ops.resume(image_name, 'image', view=view, details_page=True)

        # Delete via more operation in details page
        image_ops.delete_image(image_name, view=view, corner_btn=False, details_page=True)
        # Resume button
        image_ops.resume(image_name, 'image', view=view)
    image_ops.check_browser_console_log()
    test_util.test_pass('Delete Resume Image Test Successful')


def env_recover():
    global image_ops
    image_ops.expunge_image(image_name)
    image_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global image_ops
    try:
        image_ops.expunge_image(image_name)
        image_ops.close()
    except:
        pass
