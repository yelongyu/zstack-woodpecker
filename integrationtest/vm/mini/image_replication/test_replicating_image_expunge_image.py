'''

New Integration test for image replication.
Delete Image while it is being replicated

@author: Legion
'''

import os
import time
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops


image_name = 'image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()


def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    conf_ops.change_global_config('image', 'deletionPolicy', 'Delay')
    bs_list = img_repl.get_bs_list()
    bs = random.choice(bs_list)

    img_repl.add_image(image_name, bs_uuid=bs.uuid, url=os.getenv('imageUrl_raw'))
    img_repl.wait_for_downloading(image_name)

    img_repl.get_image_inv(image_name)
    img_repl.delete_image()
    try:
        img_repl.expunge_image()
    except:
        test_util.test_fail('It seemed that the image was expunged when delete it, this is not expected!')

    time.sleep(30)

    img_repl.check_image_data(image_name, expunged=True)
    test_util.test_pass('Create VM during Image Replicating Test Success')
    img_repl.clean_on_expunge()


def env_recover():
    img_repl.reclaim_space_from_bs()
    try:
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
