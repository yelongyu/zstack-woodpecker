'''

New Integration Test for migrate between clusters

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
data_migration = test_stub.DataMigration()

def test():
    data_migration.create_vm()
    data_migration.longjob_migr_vm()
    data_migration.vm.destroy()
    test_util.test_pass('Migrate VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if data_migration.vm:
        try:
            data_migration.vm.destroy()
        except:
            pass
