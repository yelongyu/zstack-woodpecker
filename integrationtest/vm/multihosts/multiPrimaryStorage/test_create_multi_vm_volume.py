'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import apibinding.inventory as inventory
import random

_config_ = {
        'timeout' : 7200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
new_ps_list = []
VM_COUNT = 1
DATA_VOLUME_NUMBER = 10


def test():
    test_util.test_dsc("Create {} vm  each with {} data volume in the first primaryStorage".format(VM_COUNT, DATA_VOLUME_NUMBER))
    ps_env = test_stub.PSEnvChecker()
    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE) 
    if ps_env.is_sb_ceph_env:
        first_ps = random.choice([ps for ps in ps_list if ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE])
        vm_list = test_stub.create_multi_vms(name_prefix='vm_in_fist_ps', count=VM_COUNT, ps_uuid=first_ps.uuid,
                                         data_volume_number=DATA_VOLUME_NUMBER, ps_uuid_for_data_vol=first_ps.uuid, bs_type='Ceph')
    else:
        first_ps = random.choice(ps_list)
        vm_list = test_stub.create_multi_vms(name_prefix='vm_in_fist_ps', count=VM_COUNT, ps_uuid=first_ps.uuid,
                                         data_volume_number=DATA_VOLUME_NUMBER, ps_uuid_for_data_vol=first_ps.uuid)
    
    for vm in vm_list:
        test_obj_dict.add_vm(vm)

    if len(ps_list) == 1:
        test_util.test_dsc("Add Another primaryStorage")
        second_ps = test_stub.add_primaryStorage(first_ps=first_ps)
        new_ps_list.append(second_ps)
    else:
        second_ps = random.choice([ps for ps in ps_list if ps.uuid != first_ps.uuid])

    test_util.test_dsc("Create {} vm  each with {} data volume in the second primaryStorage".format(VM_COUNT, DATA_VOLUME_NUMBER))
    if ps_env.is_sb_ceph_env:
        vm_list = test_stub.create_multi_vms(name_prefix='vm_in_second_ps', count=VM_COUNT, ps_uuid=second_ps.uuid,
                                             data_volume_number=DATA_VOLUME_NUMBER, ps_uuid_for_data_vol=second_ps.uuid, bs_type='ImageStoreBackupStorage')
    else:
        vm_list = test_stub.create_multi_vms(name_prefix='vm_in_second_ps', count=VM_COUNT, ps_uuid=second_ps.uuid,
                                             data_volume_number=DATA_VOLUME_NUMBER, ps_uuid_for_data_vol=second_ps.uuid)
    for vm in vm_list:
        test_obj_dict.add_vm(vm)

    test_util.test_dsc("Create one more vm in the first primaryStorage")
    vm = test_stub.create_multi_vms(name_prefix='test_vm', count=1, ps_uuid=first_ps.uuid)[0]
    test_obj_dict.add_vm(vm)

    test_util.test_dsc("Check the capacity")
    #To do


    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_util.test_dsc("Destroy test object")
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)

