'''

New Integration Test for hybrid.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import os

postfix = time.strftime('%m%d-%H%M%S', time.localtime())
test_obj_dict = test_state.TestStateDict()
remote_bucket_name = 'test-bucket-%s' % postfix
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.add_datacenter_iz(add_datacenter_only=True)
    hybrid.add_bucket()
    hybrid.detach_bucket()
    hybrid.attach_bucket()
    test_util.test_pass('Create Attach Detach OSS Bucket Test Success')

def env_recover():
    if hybrid.oss_bucket_create:
        hybrid.del_bucket()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
