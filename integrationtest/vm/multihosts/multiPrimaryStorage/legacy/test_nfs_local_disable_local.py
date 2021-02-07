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
VM_COUNT = 1
VOLUME_NUMBER = 10
disabled_ps_list = []


@test_lib.deprecated_case
def test():
    ps_env = test_stub.PSEnvChecker()

    local_ps = ps_env.get_random_local()
    nfs_ps = ps_env.get_random_nfs()

    test_util.test_dsc("Create {0} vm ".format(VM_COUNT))
    vm = test_stub.create_multi_vms(name_prefix='test-', count=VM_COUNT)[0]
    vm.check()
    test_obj_dict.add_vm(vm)

    test_util.test_dsc("Create {0} volumes in NFS".format(VOLUME_NUMBER))
    volume_in_nfs = test_stub.create_multi_volumes(count=VOLUME_NUMBER, ps=nfs_ps)
    for volume in volume_in_nfs:
        test_obj_dict.add_volume(volume)
        volume.check()

    test_util.test_dsc("Attach all volumes to VM")
    for volume in volume_in_nfs:
        volume.attach(vm)
        volume.check()

    test_util.test_dsc("disable local PS")
    ps_ops.change_primary_storage_state(local_ps.uuid, state='disable')
    disabled_ps_list.append(local_ps)

    test_util.test_dsc("make sure all VM and Volumes still OK and running")
    vm.check()
    for volume in volume_in_nfs:
        volume.check()

    test_util.test_dsc("Try to create vm with datavolume")
    with test_stub.expected_failure('Create vm with datavol in nfs-local env when local disabled', Exception):
        test_stub.create_multi_vms(name_prefix='test-vm', count=1, datavolume=10)

    test_util.test_dsc("Try to create datavolume in NFS")
    volume = test_stub.create_multi_volumes(count=1, ps=nfs_ps)[0]
    test_obj_dict.add_volume(volume)

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    for disabled_ps in disabled_ps_list:
        ps_ops.change_primary_storage_state(disabled_ps.uuid, state='enable')