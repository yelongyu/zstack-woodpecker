'''

New Integration Test for migrate between clusters

@author: Legion
'''

import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
data_migration = test_stub.DataMigration()

def test():
    data_migration.create_vm()
    test_obj_dict.add_vm(data_migration.vm)

    snapshots = test_obj_dict.get_volume_snapshot(data_migration.root_vol_uuid)
    snapshots.set_utility_vm(data_migration.vm)
    snapshots.create_snapshot('create_root_snapshot1')
    snapshots.check()
    snapshot1 = snapshots.get_current_snapshot()

    # data to check will be in snapshot2
    data_migration.copy_data()
    time.sleep(5)
    snapshots.create_snapshot('create_root_snapshot2')
    snapshots.check()
    snapshot2 = snapshots.get_current_snapshot()

    # revert sp
    data_migration.vm.stop()
    snapshots.use_snapshot(snapshot1)

    time.sleep(5)
    data_migration.migrate_vm()

    data_migration.vm.stop()
    snapshots.use_snapshot(snapshot2)
    data_migration.vm.start()
    data_migration.vm.check()
    data_migration.check_data()

    snapshots.create_snapshot('create_snapshot1.1.1')
    snapshots.check()

    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create Snapshot of Migrated VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
