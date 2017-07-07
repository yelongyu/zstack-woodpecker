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
DATA_VOLUME_NUMBER = 10


def test():
    if not (test_stub.find_ps_local() and test_stub.find_ps_nfs()):
        test_util.test_skip("Skip test if not local-nfs multi ps environment")

    test_util.test_dsc("Create {} vm each with {} data volume".format(VM_COUNT, DATA_VOLUME_NUMBER))
    vm_list = test_stub.create_multi_vms(name_prefix='test-', count=VM_COUNT, data_volume_number=DATA_VOLUME_NUMBER)
    for vm in vm_list:
        test_obj_dict.add_vm(vm)

    test_util.test_dsc("Check all root volumes in LOCAL PS, all data volumes in NFS PS")
    for vm in vm_list:
        root_volume = test_lib.lib_get_root_volume(vm.get_vm())
        ps_uuid = root_volume.primaryStorageUuid
        ps = res_ops.get_resource(res_ops.PRIMARY_STORAGE, uuid=ps_uuid)[0]
        assert ps.type == inventory.LOCAL_STORAGE_TYPE

        data_volume_list = [vol for vol in vm.get_vm().allVolumes if vol.type != 'Root']
        for date_volume in data_volume_list:
            ps_uuid = date_volume.primaryStorageUuid
            ps = res_ops.get_resource(res_ops.PRIMARY_STORAGE, uuid=ps_uuid)[0]
            assert ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
