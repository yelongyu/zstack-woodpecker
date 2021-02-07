'''

New Integration Test for migrate resize data volume from ceph to xsky 

@author: YeTian
@DATE:  2019-02-19
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
    new_size = 2*1024*1024*1024
    data_migration.resize_data_volume(new_size)
    data_migration.mount_disk_in_vm()
    data_migration.copy_data()

    data_migration.data_volume.detach()
    data_migration.migrate_vm()
    data_migration.migrate_data_volume()

    test_obj_dict.add_vm(data_migration.vm)
    test_obj_dict.add_volume(data_migration.data_volume)
    data_migration.data_volume.attach(data_migration.vm)
    data_migration.mount_disk_in_vm()
    data_migration.check_data()
    data_migration.check_origin_data_exist(root_vol=False)
    data_migration.clean_up_ps_trash_and_check()

#     data_migration.del_obsoleted_data_volume()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Migrate resize Data Volume Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
