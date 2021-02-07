'''

New Integration Test for migrate between clusters

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import apibinding.inventory as inventory
import zstackwoodpecker.operations.resource_operations as res_ops

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
data_migration = test_stub.DataMigration()

def test():
    bs_list = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for bs in bs_list:
        if bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
            break
    else:
        test_util.test_logger('BS is type %s, skip.' % bs.type)
    data_migration.migrate_image()
    data_migration.check_origin_image_exist()
    data_migration.clean_up_single_image_trash()
    test_util.test_pass('Cleanup Single Image Trash Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if data_migration.vm:
        try:
            data_migration.vm.destroy()
        except:
            pass
