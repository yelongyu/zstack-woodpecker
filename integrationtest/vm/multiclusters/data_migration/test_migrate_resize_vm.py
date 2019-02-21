'''

New Integration Test for migrate rezise vm from ceph to xsky

@author: YeTian
@Date:   2019-02-18
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

    new_size = 5*1024*1024*1024
    data_migration.resize_vm(new_size)

    data_migration.copy_data()
    data_migration.migrate_vm()
    data_migration.check_data()

    data_migration.check_origin_data_exist()
    data_migration.clean_up_ps_trash_and_check()

    data_migration.vm.stop()
    data_migration.vm.start()

    #delay start vm
    data_migration.vm.start()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create vm and resize vm  Migrated VM from ceph to xsky Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

