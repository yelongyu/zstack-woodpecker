'''

New Integration Test for Ceph Pool Capacity.

@author: Legion
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
pool_cap = test_stub.PoolCapacity()


def test():
    pool_cap.add_image()
    time.sleep(300)
    pool_cap.get_bs()
    used1 = pool_cap.bs.poolUsedCapacity
    avail1 = pool_cap.bs.poolAvailableCapacity
    pool_cap.check_pool_cap([used1, avail1], bs=True)

    pool_cap.del_image()
    time.sleep(300)
    pool_cap.get_bs()
    used2 = pool_cap.bs.poolUsedCapacity
    avail2 = pool_cap.bs.poolAvailableCapacity
    pool_cap.check_pool_cap([used2, avail2], bs=True)
    test_util.test_pass('Ceph Image Pool Capacity Test Success')


#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
