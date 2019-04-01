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
data_migration = test_stub.DataMigration()

def test():
    data_migration.create_vm(data_migration.image_name_net)
    test_obj_dict.add_vm(data_migration.vm)

    for i in range(20):
        data_migration.create_snapshot()
        if i % 3 == 2:
            data_migration.revert_sp()

    data_migration.sp_check()
    data_migration.batch_del_sp()

    for i in range(10):
        data_migration.create_snapshot()
        if i % 2 == 1:
            data_migration.revert_sp()

    data_migration.sp_check()
    data_migration.batch_del_sp()
    data_migration.migrate_vm()

    for i in range(20):
        data_migration.create_snapshot()
        if i % 3 == 2:
            data_migration.revert_sp()

    data_migration.sp_check()
    data_migration.batch_del_sp()

    data_migration.vm.destroy()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Batch Delete VM Snapshot after Migrating VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(data_migration.test_obj_dict)
