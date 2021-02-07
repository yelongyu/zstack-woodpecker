'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import time
import apibinding.inventory as inventory


_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VOLUME_NUMBER = 10
maintenance_ps_list = []


@test_stub.skip_if_only_one_ps
def test():
    ps_env = test_stub.PSEnvChecker()

    ps1, ps2 = ps_env.get_two_ps()

    vm_list = []
    for root_vol_ps in [ps1, ps2]:
        for data_vol_ps in [ps1, ps2]:
            if root_vol_ps.type == "SharedBlock":
                bs_type = "ImageStoreBackupStorage"
            elif root_vol_ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:
                bs_type = "Ceph"
            else:
                bs_type = None
            vm = test_stub.create_multi_vms(name_prefix='test_vm', count=1,
                                            ps_uuid=root_vol_ps.uuid, data_volume_number=VOLUME_NUMBER,
                                            ps_uuid_for_data_vol=data_vol_ps.uuid, timeout=1800000, bs_type=bs_type)[0]
            test_obj_dict.add_vm(vm)
            vm_list.append(vm)

    vm1, vm2, vm3, vm4 = vm_list

    for vm in vm_list:
        ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")

    ps_ops.change_primary_storage_state(state='maintain', primary_storage_uuid=ps2.uuid)
    maintenance_ps_list.append(ps2)
    time.sleep(60)

    vr_vm_list = test_lib.lib_find_vr_by_vm(vm1.get_vm())
    vr_vm = None
    if vr_vm_list:
        vr_vm = vr_vm_list[0]
        if vr_vm.allVolumes[0].primaryStorageUuid == ps2.uuid:
            assert vr_vm.state == inventory.STOPPED or vr_vm.state == inventory.STOPPING
        else:
            assert vr_vm.state == inventory.RUNNING
            vm1.check()
    else:
        vm1.check()

    for vm in vm_list:
        vm.update()

    assert vm1.get_vm().state == inventory.RUNNING
    assert vm2.get_vm().state == inventory.STOPPED
    assert vm3.get_vm().state == inventory.STOPPED
    assert vm4.get_vm().state == inventory.STOPPED

    for vm in [vm2, vm3, vm4]:
        with test_stub.expected_failure("start vm in maintenance ps", Exception):
            vm.start()

    test_util.test_dsc('enable ps2')
    ps_ops.change_primary_storage_state(state='enable', primary_storage_uuid=ps2.uuid)
    maintenance_ps_list.remove(ps2)

    if vr_vm and vr_vm.state == inventory.STOPPED:
        vm_ops.start_vm(vr_vm.uuid)

    time.sleep(10)
    for vm in [vm2, vm3, vm4]:
        vm.start()

    for vm in [vm2, vm3, vm4]:
        vm.update()
        vm.check()

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    for maintenance_ps in maintenance_ps_list:
        ps_ops.change_primary_storage_state(maintenance_ps.uuid, state='enable')
    test_lib.lib_error_cleanup(test_obj_dict)
