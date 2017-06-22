'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.volume_operations as vol_ops

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VOLUME_NUMBER = 10
disabled_ps_list = []


def test():
    local_nfs_env = False
    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    local_ps = test_stub.find_ps_local()
    another_ps = [ps for ps in ps_list if not ps is local_ps][0]
    if test_stub.find_ps_nfs():
        local_nfs_env = True

    vm = test_stub.create_multi_vms(name_prefix='test-', count=1)[0]
    test_obj_dict.add_vm(vm)
    vm.check()

    volume_in_local = test_stub.create_multi_volume(count=VOLUME_NUMBER, ps=local_ps,
                                                    host_uuid=test_lib.lib_get_vm_host(vm.get_vm()).uuid)

    if local_nfs_env:
        volume_in_another = test_stub.create_multi_volume(count=VOLUME_NUMBER, ps=another_ps)
    else:
        volume_in_another = test_stub.create_multi_volume(count=VOLUME_NUMBER, ps=another_ps,
                                                          host_uuid=test_lib.lib_get_vm_host(vm.get_vm()).uuid)

    for volume in volume_in_local + volume_in_another:
        test_obj_dict.add_volume(volume)

    for volume in volume_in_local + volume_in_another:
        volume.attach(vm)
        volume.check()
    vm.check()

    for volume in volume_in_local + volume_in_another:
        volume.detach()
        volume.check()
    vm.check()

    target_host = test_lib.lib_find_random_host_by_volume_uuid(test_lib.lib_get_root_volume(vm.get_vm()).uuid)
    target_host_uuid = target_host.uuid

    vm.stop()
    vm.check()
    vol_ops.migrate_volume(test_lib.lib_get_root_volume(vm.get_vm()).uuid, target_host_uuid)

    for volume in volume_in_local:
        vol_ops.migrate_volume(volume.get_volume().uuid, target_host_uuid)

    if not local_nfs_env:
        for volume in volume_in_another:
            vol_ops.migrate_volume(volume.get_volume().uuid, target_host_uuid)

    for volume in volume_in_local + volume_in_another:
        volume.attach(vm)
        volume.check()

    vm.start()
    vm.check()

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    for disabled_ps in disabled_ps_list:
        ps_ops.change_primary_storage_state(disabled_ps.uuid, state='enable')