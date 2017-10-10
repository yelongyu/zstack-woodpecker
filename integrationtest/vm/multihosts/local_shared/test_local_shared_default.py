'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os


_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()



case_flavor = dict(ps_enabled=      dict(local_enable=True, shared_enable=True),
                   disable_shared=  dict(local_enable=True, shared_enable=False),
                   disable_local=   dict(local_enable=False, shared_enable=True),
                   disable_both=    dict(local_enable=False, shared_enable=False),

                   )


@test_stub.skip_if_not_local_shared
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    ps_env = test_stub.PSEnvChecker()
    local_ps, shared_ps = ps_env.get_two_ps()

    test_util.test_dsc("Try to Create VM without specified ps")
    if flavor['local_enable'] or flavor['shared_enable']:
        vm_list = test_stub.create_multi_vms(name_prefix='test-vm', count=10)
        for vm in vm_list:
            if flavor['local_enable']:
                assert test_lib.lib_get_root_volume(vm).primaryStorageUuid == local_ps.uuid
            else:
                assert test_lib.lib_get_root_volume(vm).primaryStorageUuid == shared_ps.uuid
    else:
        with test_lib.expected_failure('Create vm when no ps enabled', Exception):
            test_stub.create_multi_vms(name_prefix='test-vm', count=1)

    test_util.test_dsc("Create VM with Volume without specified ps")
    if flavor['local_enable'] or flavor['shared_enable']:
        vm_list = test_stub.create_multi_vms(name_prefix='test-vm', count=10, data_volume_number=1)
        for vm in vm_list:
            if flavor['local_enable']:
                assert test_lib.lib_get_root_volume(vm).primaryStorageUuid == local_ps.uuid
            else:
                assert test_lib.lib_get_root_volume(vm).primaryStorageUuid == shared_ps.uuid

            for data_vol in [volume for volume in vm.get_vm().allVolumes if volume.type != 'Root']:
                if flavor['shared_enable']:
                    assert data_vol.primaryStorageUuid == shared_ps.uuid
                else:
                    assert data_vol.primaryStorageUuid == local_ps.uuid
    else:
        with test_lib.expected_failure('Create vm with volume when no ps enabled', Exception):
            test_stub.create_multi_vms(name_prefix='test-vm', count=10, data_volume_number=1)



def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)