'''

New Integration test for image replication.

@author: Legion
'''

import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

image_name = 'iso-image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()


def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    img_repl.add_iso_image(image_name)
    img_repl.wait_for_image_replicated(image_name)
    img_repl.check_image_data(image_name)
    img_repl.reconnect_host()
    img_repl.create_iso_vm()
    test_util.test_pass('ISO Image Replication Test Success')


def env_recover():
    img_repl.delete_image()
    img_repl.expunge_image()
    img_repl.reclaim_space_from_bs()


#Will be called only if exception happens in test().
def error_cleanup():
    img_repl.delete_image()
    img_repl.expunge_image()
    img_repl.reclaim_space_from_bs()
