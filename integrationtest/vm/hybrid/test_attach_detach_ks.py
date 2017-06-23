'''

Test attach/detach Aliyun key & secret.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import os

test_obj_dict = test_state.TestStateDict()
ks_inv = None


def test():
    global ks_inv
    global datacenter_inv
    ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    hyb_ops.detach_aliyun_key(ks_inv.uuid)
    ks_detach = hyb_ops.query_aliyun_key_secret()
    assert ks_detach[0].current == 'false'
    hyb_ops.attach_aliyun_key(ks_inv.uuid)
    ks_attach = hyb_ops.query_aliyun_key_secret()
    assert ks_attach[0].current == 'true'
    test_util.test_pass('Detach Attach Aliyun key and secret success')

def env_recover():
    global ks_inv
    if ks_inv:
        hyb_ops.del_aliyun_key_secret(ks_inv.uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
