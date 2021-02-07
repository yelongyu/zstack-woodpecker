'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VOLUME_NUMBER = 10


@test_lib.deprecated_case
def test():
    ps_env = test_stub.PSEnvChecker()

    nfs_ps = ps_env.get_random_nfs()

    vm = test_stub.create_multi_vms(name_prefix='test-', count=1)[0]
    volume_list = test_stub.create_multi_volumes(count=VOLUME_NUMBER, ps=nfs_ps)

    test_util.test_dsc("Attach all volumes to local ps vm")
    for volume in volume_list:
        volume.attach(vm)

    for volume in volume_list:
        volume.check()

    for volume in volume_list:
        volume.detach()

    for volume in volume_list:
        volume.check()

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)

