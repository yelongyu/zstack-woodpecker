'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VM_COUNT = 1
VOLUME_NUMBER = 10


@test_lib.deprecated_case
def test():
    ps_env = test_stub.PSEnvChecker()
    nfs_ps = ps_env.get_random_nfs()

    volume_list = test_stub.create_multi_volumes(count=VOLUME_NUMBER, ps=nfs_ps)
    for volume in volume_list:
        test_obj_dict.add_volume(volume)
        volume.check()
    for volume in volume_list:
        assert volume.get_volume().primaryStorageUuid == nfs_ps.uuid

    with test_stub.expected_failure('Create volume on local in local-nfs environment', Exception):
        test_stub.create_multi_volumes(count=1, ps=ps_env.get_random_local())

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
