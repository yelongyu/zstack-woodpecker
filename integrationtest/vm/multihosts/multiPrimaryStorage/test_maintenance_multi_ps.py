'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import time
import apibinding.inventory as inventory

_config_ = {
        'timeout' : 7200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VOLUME_NUMBER = 10
maintenance_ps_list = []


@test_stub.skip_if_only_one_ps
def test():
    ps_env = test_stub.PSEnvChecker()

    ps, another_ps = ps_env.get_two_ps()

    if ps_env.is_sb_ceph_env:
        vm1, vm2 = test_stub.create_multi_vms(name_prefix='test-', count=2, ps_uuid=ps.uuid, timeout=600000, bs_type='ImageStoreBackupStorage')
    else:
        vm1, vm2 = test_stub.create_multi_vms(name_prefix='test-', count=2, ps_uuid=ps.uuid, timeout=600000)

    for vm in (vm1, vm2):
        test_obj_dict.add_vm(vm)

    volume_in_another = test_stub.create_multi_volumes(count=VOLUME_NUMBER, ps=another_ps,
                                                       host_uuid=test_lib.lib_get_vm_host(vm2.get_vm()).uuid
                                                       if another_ps.type == inventory.LOCAL_STORAGE_TYPE else None)
    for volume in volume_in_another:
        test_obj_dict.add_volume(volume)

    for volume in volume_in_another:
        volume.attach(vm2)

    test_util.test_dsc('set another ps in maintenance mode')
    ps_ops.change_primary_storage_state(state='maintain', primary_storage_uuid=another_ps.uuid)
    maintenance_ps_list.append(another_ps)

    test_stub.wait_until_vm_reach_state(120, inventory.STOPPED, vm2)
    vm1.update()
    assert vm1.get_vm().state == inventory.RUNNING

    vr_vm_list = test_lib.lib_find_vr_by_vm(vm1.get_vm())
    vr_vm = None
    if vr_vm_list:
        vr_vm = vr_vm_list[0]
        if vr_vm.allVolumes[0].primaryStorageUuid == another_ps.uuid:
            assert vr_vm.state == inventory.STOPPED  or vr_vm.state == inventory.STOPPING
        else:
            assert vr_vm.state == inventory.RUNNING
            vm1.check()
    else:
        vm1.check()

    with test_stub.expected_failure("Start vm in maintenance ps", Exception):
        vm2.start()

    test_util.test_dsc('enable another ps')
    ps_ops.change_primary_storage_state(state='enable', primary_storage_uuid=another_ps.uuid)
    maintenance_ps_list.remove(another_ps)

    if vr_vm and vr_vm.state == inventory.STOPPED:
        vm_ops.start_vm(vr_vm.uuid)

    time.sleep(10)
    vm2.start()
    vm2.check()

    for volume in volume_in_another:
        volume.detach()
        volume.attach(vm2)

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    for maintenance_ps in maintenance_ps_list:
        ps_ops.change_primary_storage_state(maintenance_ps.uuid, state='enable')
    test_lib.lib_error_cleanup(test_obj_dict)
