'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
new_ps_list = []
VM_COUNT = 10
VOLUME_NUMBER = 10


def test():
    if not (test_stub.find_ps_local() and test_stub.find_ps_nfs()):
        test_util.test_skip("Skip test if not local-nfs multi ps environment")

    local_ps = test_stub.find_ps_local()
    nfs_ps = test_stub.find_ps_nfs()

    volume_list = test_stub.create_multi_volume(count=VOLUME_NUMBER, ps=nfs_ps)
    for volume in volume_list:
        test_obj_dict.add_volume(volume)
        volume.check()
    for volume in volume_list:
        assert volume.get_volume().primaryStorageUuid == nfs_ps.uuid

    with test_stub.expect_failure('Create vm on nfs in local-nfs environment', Exception):
        test_stub.create_multi_volume(count=1, ps=local_ps)

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)