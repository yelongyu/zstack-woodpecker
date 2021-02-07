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
from threading import Thread


image_name = 'image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()
vm_thrd_list = []
vm_list = []

class CRTVMThread(Thread):
    def __init__(self, func, args=()):
        super(CRTVMThread,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.vm = self.func(*self.args)

    def get_vm(self):
        return self.vm

def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    bs_list = img_repl.get_bs_list()
    bs = random.choice(bs_list)

    for n in range(1,4):
        vm_thrd_list.append(CRTVMThread(func=img_repl.create_vm, args=(image_name, 'image-replication-test-vm' + '-' + str(n))))

    img_repl.add_image(image_name, bs_uuid=bs.uuid, url=os.getenv('imageUrl_raw'))
    img_repl.wait_for_downloading(image_name)

    for vm_thrd in vm_thrd_list:
        vm_thrd.start()
    for vmthrd in vm_thrd_list:
        vmthrd.join()
        vm_list.append(vmthrd.get_vm())
    img_repl.wait_for_image_replicated(image_name)
    test_util.test_pass('Batch Create VM during Image Replicating Test Success')
    img_repl.clean_on_expunge()


def env_recover():
    img_repl.delete_image()
    img_repl.expunge_image()
    img_repl.reclaim_space_from_bs()
    try:
        for vm in vm_list:
            vm.destroy()
    except:
        pass


#Will be called only if exception happens in test().
def error_cleanup():
    try:
        img_repl.delete_image()
        img_repl.expunge_image()
        img_repl.reclaim_space_from_bs()
        for vm in vm_list:
            vm.destroy()
    except:
        pass
