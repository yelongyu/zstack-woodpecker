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
    data_migration.create_vm(data_migration.image_name_net)
    data_migration.create_data_volume()

    data_migration.data_volume.detach()
    data_migration.migrate_vm()
    data_migration.longjob_migr_data_vol()

    test_obj_dict.add_vm(data_migration.vm)
    test_obj_dict.add_volume(data_migration.data_volume)
    data_migration.data_volume.attach(data_migration.vm)

#     data_migration.del_obsoleted_data_volume()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Migrate Data Volume Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
