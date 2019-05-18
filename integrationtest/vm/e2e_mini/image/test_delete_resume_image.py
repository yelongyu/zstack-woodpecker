# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
image_name = 'image-' + test_stub.get_time_postfix()

def test():
    global mini
    mini = test_stub.MINI()
    mini.add_image(name=image_name)

    for view in ['card', 'list']:
        # Delete button
        mini.delete_image(image_name, view=view)
        # Resume button
        mini.resume(image_name, 'image', view=view)

        # Delete via more operation
        mini.delete_image(image_name, view=view, corner_btn=False)
        # Resume by more ops
        mini.resume(image_name, 'image', view=view, details_page=True)

        # Delete via more operation in details page
        mini.delete_image(image_name, view=view, corner_btn=False, details_page=True)
        # Resume button
        mini.resume(image_name, 'image', view=view)
    mini.check_browser_console_log()
    test_util.test_pass('Delete Resume Image Test Successful')


def env_recover():
    global mini
    mini.expunge_image(image_name)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.expunge_image(image_name)
        mini.close()
    except:
        pass
