'''

New Integration Test for Batch Deleting Snapshot.

@author: Legion
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
bat_del_sp = test_stub.BATCHDELSP()


def test():
    bat_del_sp.create_vm()
    bat_del_sp.create_data_volume()
    for i in range(20):
        bat_del_sp.create_sp()
        if i % 3 == 2:
            bat_del_sp.revert_sp(root_vol=False)

    bat_del_sp.sp_check()
    bat_del_sp.batch_del_sp()

    for i in range(10):
        bat_del_sp.create_sp()
        if i % 2 == 1:
            bat_del_sp.revert_sp(root_vol=False)

    bat_del_sp.sp_check()
    bat_del_sp.batch_del_sp()

    test_util.test_pass('Batch Delete VM Snapshot Test Successful')


#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(bat_del_sp.test_obj_dict)
