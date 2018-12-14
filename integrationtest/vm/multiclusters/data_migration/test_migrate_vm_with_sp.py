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
    
    test_obj_dict.add_vm(data_migration.vm)

    snapshots = test_obj_dict.get_volume_snapshot(data_migration.root_vol_uuid)
    snapshots.set_utility_vm(data_migration.vm)
    snapshots.create_snapshot('create_root_snapshot1')
    snapshots.check()
    snapshot1 = snapshots.get_current_snapshot()

    snapshots.create_snapshot('create_root_snapshot2')
    snapshots.check()
    snapshot2 = snapshots.get_current_snapshot()

    snapshots.create_snapshot('create_root_snapshot3')
    snapshots.check()
    snapshot3 = snapshots.get_current_snapshot()

    data_migration.copy_data()
    data_migration.migrate_vm()
    data_migration.check_data()

    data_migration.check_origin_data_exist()
    data_migration.clean_up_ps_trash_and_check()
    data_migration.check_vol_sp(data_migration.root_vol_uuid, 3)

    snapshots.delete_snapshot(snapshot1)
    snapshots.delete_snapshot(snapshot2)
    snapshots.delete_snapshot(snapshot3)
    test_obj_dict.rm_volume_snapshot(snapshots)
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create Snapshot of Migrated VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
