'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.header.host as host_header
import os
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import random

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():

    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    if len(ps_list) < 2:
        test_util.test_skip("Skip test if less than two Primary Storage")

    l3_name = os.environ.get('l3VlanNetworkName1')

    vm1 = test_stub.create_vm_with_random_offering(vm_name='vm', l3_name=l3_name)
    test_obj_dict.add_vm(vm1)

    disk_offering_uuids = [random.choice(res_ops.get_resource(res_ops.DISK_OFFERING)).uuid]
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vm_with_data_vol',
                                                   disk_offering_uuids=disk_offering_uuids,
                                                   l3_name=l3_name)
    test_obj_dict.add_vm(vm2)

    ps, another = test_stub.get_ps_vm_creation()

    vm3 = test_stub.create_vm_with_random_offering(vm_name='vm_with_data_vol_specified_ps1',
                                                   disk_offering_uuids=disk_offering_uuids,
                                                   ps_uuid=ps.uuid,
                                                   l3_name=l3_name)
    test_obj_dict.add_vm(vm3)

    root_vol_vm3 = test_lib.lib_get_root_volume(vm3.get_vm())
    assert root_vol_vm3.primaryStorageUuid == ps.uuid

    vm4 = test_stub.create_vm_with_random_offering(vm_name='vm_with_data_vol_specified_ps2',
                                                   disk_offering_uuids=disk_offering_uuids,
                                                   l3_name=l3_name,
                                                   system_tags=['primaryStorageUuidForDataVolume::{}'.format(another.uuid)])
    test_obj_dict.add_vm(vm4)

    data_vol_list_vm4 = [vol for vol in vm4.get_vm().allVolumes if vol.type != 'Root']
    for data_vol in data_vol_list_vm4:
        assert data_vol.primaryStorageUuid == another.uuid

    vm5 = test_stub.create_vm_with_random_offering(vm_name='vm_with_data_vol_specified_ps3',
                                                   disk_offering_uuids=disk_offering_uuids,
                                                   ps_uuid=ps.uuid,
                                                   l3_name=l3_name,
                                                   system_tags=['primaryStorageUuidForDataVolume::{}'.format(another.uuid)])
    test_obj_dict.add_vm(vm5)

    root_vol_vm5 = test_lib.lib_get_root_volume(vm5.get_vm())
    assert root_vol_vm5.primaryStorageUuid == ps.uuid
    data_vol_list_vm5 = [vol for vol in vm5.get_vm().allVolumes if vol.type != 'Root']
    for data_vol in data_vol_list_vm5:
        assert data_vol.primaryStorageUuid == another.uuid

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)

