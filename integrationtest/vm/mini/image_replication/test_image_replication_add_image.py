'''

New Integration test for image replication.

@author: Legion
'''

import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

image_name = 'image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub_vr = test_lib.lib_get_test_stub('virtualrouter')
longjob = test_stub_vr.Longjob(name=image_name, url=os.getenv('imageUrl_vdbench'))
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()


def test():
    longjob.add_image()
    img_repl.wait_for_image_replicated(image_name)
    img_repl.check_image_data(image_name)
    test_util.test_pass('Image Replication Test Success')


def env_recover():
    longjob.delete_image()


#Will be called only if exception happens in test().
def error_cleanup():
    longjob.delete_image()
