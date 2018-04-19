'''

New Integration Test for Ceph Pool Capacity.

@author: Legion
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
pool_cap = test_stub.PoolCapacity()


def test():
    pool_cap.get_bs()
    pool_cap.get_replicated_size()
    pool_cap.check_pool_replicated_size()
    test_util.test_pass('Pool Replicated Size Test Success')


#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
