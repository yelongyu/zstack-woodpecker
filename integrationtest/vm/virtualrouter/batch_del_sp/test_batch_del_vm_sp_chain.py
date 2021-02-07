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
bat_del_sp = test_stub.BATCHDELSP('create_vm', 50)


def test():
    bat_del_sp.make_chain()
    test_util.test_dsc('Current test chain is %s' % bat_del_sp.test_list)
    bat_del_sp.run_test()
    test_util.test_pass('Batch Deleting Volume Snapshot Chain: %s Test Success' % bat_del_sp.test_list)


#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(bat_del_sp.test_obj_dict)
