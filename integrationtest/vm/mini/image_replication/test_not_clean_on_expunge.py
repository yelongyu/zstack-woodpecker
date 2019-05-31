'''

New Integration test for image replication.

@author: Legion
'''

import os
import time
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

image_name = 'iso-image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()


def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    conf_ops.change_global_config('imagestore', 'cleanOnExpunge', 'false')
    bs_list = img_repl.get_bs_list()
    bs = random.choice(bs_list)

    img_repl.add_image(image_name, bs_uuid=bs.uuid, img_format='iso')
    img_repl.wait_for_image_replicated(image_name)
    img_repl.check_image_data(image_name)

    img_repl.delete_image()
    img_repl.expunge_image()

    time.sleep(20)

    img_repl.check_image_data(image_name)

    test_util.test_pass('Global config cleanOnExpunge Test Success')


def env_recover():
    img_repl.reclaim_space_from_bs()
    try:
        img_repl.delete_image()
        img_repl.expunge_image()
        img_repl.vm.destroy()
    except:
        pass


#Will be called only if exception happens in test().
def error_cleanup():
    try:
        img_repl.delete_image()
        img_repl.expunge_image()
        img_repl.reclaim_space_from_bs()
        img_repl.vm.destroy()
    except:
        pass