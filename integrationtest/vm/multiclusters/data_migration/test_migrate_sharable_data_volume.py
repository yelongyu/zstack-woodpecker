'''

New Integration Test for migrate between clusters

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import time

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
data_migration = test_stub.DataMigration()

def test():
    vm1 = data_migration.create_vm(data_migration.image_name_net).vm
    vm2 = data_migration.create_vm(data_migration.image_name_net).vm
    data_migration.create_data_volume(sharable=True, vms=[vm1, vm2])

    data_migration.data_volume.detach(vm1.get_vm().uuid)
    data_migration.data_volume.detach(vm2.get_vm().uuid)
    vm1, vm2 = data_migration.migrate_vm(vms=[vm1, vm2])
    data_migration.migrate_data_volume()

    test_obj_dict.add_vm(vm1)
    test_obj_dict.add_vm(vm2)
    test_obj_dict.add_volume(data_migration.data_volume)
    data_migration.data_volume.attach(vm1)
    data_migration.data_volume.attach(vm2)
    data_migration.data_volume.check()

    time.sleep(30)
    data_migration.data_volume.detach(vm1.get_vm().uuid)
    data_migration.data_volume.detach(vm2.get_vm().uuid)
    data_migration.data_volume.check()

#     data_migration.del_obsoleted_data_volume()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Migrate Data Volume Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
