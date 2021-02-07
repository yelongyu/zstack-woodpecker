'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import random

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VOLUME_NUMBER = 1
disabled_ps_list = []


@test_stub.skip_if_multi_nfs
@test_stub.skip_if_only_one_ps
@test_stub.skip_if_not_have_local
def test():
    ps_env = test_stub.PSEnvChecker()

    local_nfs_env = ps_env.is_local_nfs_env
    local_smp_env = ps_env.is_local_smp_env

    local_ps, another_ps = ps_env.get_two_ps()

    vm = test_stub.create_multi_vms(name_prefix='test-', count=1)[0]
    test_obj_dict.add_vm(vm)
    vm.check()

    volume_in_local = test_stub.create_multi_volumes(count=VOLUME_NUMBER, ps=local_ps,
                                                    host_uuid=test_lib.lib_get_vm_host(vm.get_vm()).uuid)

    volume_in_another = test_stub.create_multi_volumes(count=VOLUME_NUMBER, ps=another_ps,
                                                       host_uuid=None if local_nfs_env else test_lib.lib_get_vm_host(vm.get_vm()).uuid)

    for volume in volume_in_local + volume_in_another:
        test_obj_dict.add_volume(volume)

    for volume in volume_in_local + volume_in_another:
        volume.attach(vm)
        volume.check()
    vm.check()
    vm.update()

    snapshots_list = []
    for volume in vm.get_vm().allVolumes:
        snapshots = test_obj_dict.get_volume_snapshot(volume.uuid)
        snapshots.set_utility_vm(vm)
        snapshots.create_snapshot('create_volume_snapshot')
        snapshots_list.append(snapshots)

    for volume in volume_in_local + volume_in_another:
        volume.detach()
        volume.check()
    vm.check()

    target_host = test_lib.lib_find_random_host(vm.get_vm())

    vm.stop()
    vm.check()
    vol_ops.migrate_volume(test_lib.lib_get_root_volume(vm.get_vm()).uuid, target_host.uuid)

    for volume in volume_in_local:
        vol_ops.migrate_volume(volume.get_volume().uuid, target_host.uuid)

    if not (local_nfs_env or local_smp_env):
        for volume in volume_in_another:
            vol_ops.migrate_volume(volume.get_volume().uuid, target_host.uuid)

    for volume in volume_in_local + volume_in_another:
        volume.attach(vm)
        volume.check()

    for snapshots in snapshots_list:
        snapshot = snapshots.get_current_snapshot()
        snapshots.use_snapshot(snapshot)

    vm.start()
    vm.check()

    for volume in volume_in_local + volume_in_another:
        assert volume.get_volume().vmInstanceUuid == vm.get_vm().uuid

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    for disabled_ps in disabled_ps_list:
        ps_ops.change_primary_storage_state(disabled_ps.uuid, state='enable')
