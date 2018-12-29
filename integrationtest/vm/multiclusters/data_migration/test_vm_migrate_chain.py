'''

New Integration Test for migrate between clusters

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_chain as test_chain
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
data_migration = test_stub.DataMigration()

def test():
    chain1 = test_chain.TestChain(data_migration)
    chain1.make_chain()
    test_util.test_dsc('Current test chain is [%s]' % chain1.test_chain)
    chain1.run_test()
    test_util.test_pass('chain1 [%s] Test Success' % chain1.test_chain)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
