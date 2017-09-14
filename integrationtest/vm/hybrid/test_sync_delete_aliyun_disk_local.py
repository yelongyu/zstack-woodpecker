'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import time

test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.add_datacenter_iz()
    hybrid.create_aliyun_disk()
    hybrid.del_aliyun_disk(remote=False)
    hybrid.sync_aliyun_disk()
    test_util.test_pass('Sync Aliyun Disk Test Success')

def env_recover():
    if hybrid.disk:
        time.sleep(50)
        hybrid.del_aliyun_disk()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
