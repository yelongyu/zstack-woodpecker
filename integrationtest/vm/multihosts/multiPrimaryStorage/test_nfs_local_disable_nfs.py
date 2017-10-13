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
VM_COUNT = 1
VOLUME_NUMBER = 10
disabled_ps_list = []


@test_lib.deprecated_case
def test():
    ps_env = test_stub.PSEnvChecker()

    nfs_ps = ps_env.get_random_nfs()

    test_util.test_dsc("Create 1 vm  with {} data volume".format(VOLUME_NUMBER))
    vm = test_stub.create_multi_vms(name_prefix='test-', count=1, data_volume_number=VOLUME_NUMBER)[0]
    test_obj_dict.add_vm(vm)

    test_util.test_dsc("disable NFS PS")
    ps_ops.change_primary_storage_state(nfs_ps.uuid, state='disable')
    disabled_ps_list.append(nfs_ps)

    test_util.test_dsc("make sure VM till OK and running")
    vm.update()
    vm.check()
    assert vm.get_vm().state == inventory.RUNNING

    with test_stub.expected_failure("Create datavol in nfs-local env when nfs disabled", Exception):
        test_stub.create_multi_volumes(count=1, ps=nfs_ps)

    test_util.test_dsc("Try to create vm")
    new_vm = test_stub.create_multi_vms(name_prefix='test-vm', count=1)[0]
    test_obj_dict.add_vm(new_vm)

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    for disabled_ps in disabled_ps_list:
        ps_ops.change_primary_storage_state(disabled_ps.uuid, state='enable')