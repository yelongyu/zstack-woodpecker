'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import random

_config_ = {
        'timeout' : 7200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


@test_stub.skip_if_only_one_ps
def test():
    ps_env = test_stub.PSEnvChecker()

    ps, another = ps_env.get_two_ps()
    disk_offering_uuids = [random.choice(res_ops.get_resource(res_ops.DISK_OFFERING)).uuid]

    vm = test_stub.create_iso_vm_with_random_offering(vm_name='iso_vm', l3_name='l3VlanNetworkName1')
    test_obj_dict.add_vm(vm)

    for root_volume_ps_uuid in [None, ps.uuid]:
        for data_vol_ps_uuid in [None, another.uuid]:
            if ps_env.is_local_shared_env or ps_env.is_sb_ceph_env:
                if type(root_volume_ps_uuid) != type(data_vol_ps_uuid):
                    continue
            vm = test_stub.create_iso_vm_with_random_offering(vm_name='test_iso_vm',
                                                              disk_offering_uuids=disk_offering_uuids if data_vol_ps_uuid else None,
                                                              ps_uuid=root_volume_ps_uuid,
                                                              l3_name='l3VlanNetworkName1',
                                                              system_tags=['primaryStorageUuidForDataVolume::{}'.format(data_vol_ps_uuid)] if data_vol_ps_uuid else None)
            if root_volume_ps_uuid:
                root_vol = test_lib.lib_get_root_volume(vm.get_vm())
                assert root_vol.primaryStorageUuid == ps.uuid

            if data_vol_ps_uuid:
                data_vol_list = [vol for vol in vm.get_vm().allVolumes if vol.type != 'Root']
                for data_vol in data_vol_list:
                    assert data_vol.primaryStorageUuid == another.uuid

            test_obj_dict.add_vm(vm)

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)

