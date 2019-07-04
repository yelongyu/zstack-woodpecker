'''

New Integration test for image replication.
Check VM Creation during Image Replicating

@author: Legion
'''

import os
import time
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib


image_name = 'image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()
cloned_vm_list = []

def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    bs_list = img_repl.get_bs_list()
    bs = random.choice(bs_list)

    img_repl.create_vm()
    img_repl.add_image(image_name, bs_uuid=bs.uuid, url=os.getenv('imageUrl_raw'))
    img_repl.wait_for_downloading(image_name)

    cloned_vm_list = img_repl.vm.clone(['cloned-vm1', 'cloned-vm2'])
    img_repl.wait_for_image_replicated(image_name)
    for vm in cloned_vm_list:
        vm.destroy()
    test_util.test_pass('Clone VM during Image Replicating Test Success')
    img_repl.clean_on_expunge()


def env_recover():
    img_repl.delete_image()
    img_repl.expunge_image()
    img_repl.reclaim_space_from_bs()
    img_repl.vm.destroy()


#Will be called only if exception happens in test().
def error_cleanup():
    try:
        img_repl.delete_image()
        img_repl.expunge_image()
        img_repl.reclaim_space_from_bs()
        img_repl.vm.destroy()
        for vm in cloned_vm_list:
            vm.destroy()
    except:
        pass
