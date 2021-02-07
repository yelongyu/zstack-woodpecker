'''

New Integration test for image replication.
Test Image Replicating while ImageStore Backup storage almost full

@author: Legion
'''

import os
import time
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
from zstacklib.utils import ssh


image_name = 'image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()
remove_file_cmd = 'rm -rf big_size_file'
bs = None
bs2 = None


def test():
    global bs
    global bs2
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    img_repl.clean_on_expunge()
    bs_list = img_repl.get_bs_list()
    bs = random.choice(bs_list)
    bs_list.remove(bs)
    bs2 = bs_list[0]

    fallocate_size = int(bs.availableCapacity) - 9169934592
    fallocate_size2 = int(bs2.availableCapacity) - 9989934592

    fallocate_cmd = 'fallocate -l %s big_size_file' % fallocate_size
    fallocate_cmd2 = 'fallocate -l %s big_size_file' % fallocate_size2

    ssh.execute(fallocate_cmd, bs.hostname, 'root', 'password', False)
    ssh.execute(fallocate_cmd2, bs2.hostname, 'root', 'password', False)

    img_repl.add_image(image_name, bs_uuid=bs.uuid, url=os.getenv('imageUrl_windows'))

    img_repl.wait_for_image_replicated(image_name)

    img_repl.delete_image()
    img_repl.expunge_image()

    time.sleep(3)

    img_repl.add_image(image_name, bs_uuid=bs.uuid, url=os.getenv('imageUrl_raw'))
    img_repl.create_vm(image_name, 'image-replication-test-vm')

    img_repl.delete_image()
    img_repl.expunge_image()

    time.sleep(3)

    img_repl.crt_vm_image('image-replication-test-root-template')
    img_repl.wait_for_image_replicated('image-replication-test-root-template')

    ssh.execute(remove_file_cmd, bs.hostname, 'root', 'password', False)
    ssh.execute(remove_file_cmd, bs2.hostname, 'root', 'password', False)

    test_util.test_pass('Batch Create VM during Image Replicating Test Success')


def env_recover():
    global bs
    global bs2
    img_repl.reclaim_space_from_bs()
    ssh.execute(remove_file_cmd, bs.hostname, 'root', 'password', False)
    ssh.execute(remove_file_cmd, bs2.hostname, 'root', 'password', False)
    try:
        img_repl.vm.destroy()
    except:
        pass


#Will be called only if exception happens in test().
def error_cleanup():
    global bs
    global bs2
    ssh.execute(remove_file_cmd, bs.hostname, 'root', 'password', False)
    ssh.execute(remove_file_cmd, bs2.hostname, 'root', 'password', False)
    try:
        img_repl.delete_image()
        img_repl.expunge_image()
        img_repl.reclaim_space_from_bs()
        img_repl.vm.destroy()
    except:
        pass
