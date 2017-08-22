'''

New Integration Test for hybrid.

@author: Legion
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
    ks_existed = hyb_ops.query_aliyun_key_secret()
    if not ks_existed:
        ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    else:
        ks_inv = ks_existed[0]
    hyb_ops.update_aliyun_key_secret(ks_inv.uuid, name='test_ks')
    assert ks_inv.name == 'test_ks'
    hyb_ops.update_aliyun_key_secret(ks_inv.uuid, description='test aliyun key secret')
    assert ks_inv.description == 'test aliyun key secret'
    test_util.test_pass('Update Aliyun Key and Secret Success')

def env_recover():
    global ks_inv
    if ks_inv:
        hyb_ops.del_aliyun_key_secret(ks_inv.uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
