'''

New Integration test for image replication.
Check Image Replication after BS recovering from powered off,
Target BS would be powered off during replicating new image 

@author: Legion
'''

import os
import time
import random
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib


image_name = 'image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()


def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    bs_list = img_repl.get_bs_list()
    bs = random.choice(bs_list)
    bs_list.remove(bs)
    bs2 = bs_list[0]

    img_repl.add_image(image_name, bs_uuid=bs.uuid, url=os.getenv('imageUrl_raw'))
    img_repl.wait_for_downloading(image_name)
    cmd = 'zsha2 demote'
    try:
        ssh.execute(cmd, bs.hostname, 'root', 'password')
    except:
        ssh.execute(cmd, bs2.hostname, 'root', 'password')

    img_repl.wait_for_image_replicated(image_name)
    img_repl.create_vm(image_name)
    test_util.test_pass('Demote node during Image Replicating Test Success')
    img_repl.clean_on_expunge()


def env_recover():
    img_repl.delete_image()
    img_repl.expunge_image()
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
