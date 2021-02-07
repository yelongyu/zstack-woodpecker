'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.test_state as test_state

test_obj_dict = test_state.TestStateDict()

def test():
    ks_existed = hyb_ops.query_hybrid_key_secret()
    if ks_existed:
        for ks in ks_existed:
            hyb_ops.del_hybrid_key_secret(ks.uuid)
    try:
        hyb_ops.add_hybrid_key_secret('test_invalid_hybrid', 'test for hybrid', 'invalid-key', 'invalid-secret')
    except hyb_ops.ApiError, e:
        err_msg = e
    assert err_msg and not hyb_ops.query_hybrid_key_secret()
    test_util.test_pass('Detach Attach Aliyun Key and Secret Success')


#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
