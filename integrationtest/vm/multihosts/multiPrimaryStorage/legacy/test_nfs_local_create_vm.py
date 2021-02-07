'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state


_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VM_COUNT = 1


@test_lib.deprecated_case
def test():

    test_util.test_dsc("Create {0} vm ".format(VM_COUNT))
    vm_list = test_stub.create_multi_vms(name_prefix='test-', count=VM_COUNT)
    for vm in vm_list:
        test_obj_dict.add_vm(vm)

    test_util.test_dsc("Check all root volumes in LOCAL PS")
    for vm in vm_list:
        ps_uuid = vm.get_vm().allVolumes[0].primaryStorageUuid
        ps = res_ops.get_resource(res_ops.PRIMARY_STORAGE, uuid=ps_uuid)[0]
        assert ps.type == inventory.LOCAL_STORAGE_TYPE

    with test_stub.expected_failure('Create vm on nfs in local-nfs environment', Exception):
        test_stub.create_multi_vms(name_prefix='test-', count=VM_COUNT, ps_uuid=test_stub.PSEnvChecker().get_random_nfs().uuid)

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
