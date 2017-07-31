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
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VOLUME_NUMBER = 10
maintenance_ps_list = []


def test():

    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    if len(ps_list) < 2:
        test_util.test_skip("Skip test if only one primary storage")
    if test_stub.find_ps_local() and test_stub.find_ps_nfs():
        test_util.test_skip("Skip test for local-nfs multi ps environment")

    ps1, ps2 = test_stub.get_ps_vm_creation()

    vm1 = test_stub.create_multi_vms(name_prefix='vm1', count=1,
                                     ps_uuid=ps1.uuid, data_volume_number=VOLUME_NUMBER,
                                     ps_uuid_for_data_vol=ps1.uuid)[0]
    vm2 = test_stub.create_multi_vms(name_prefix='vm2', count=1,
                                     ps_uuid=ps1.uuid, data_volume_number=VOLUME_NUMBER,
                                     ps_uuid_for_data_vol=ps2.uuid)[0]
    vm3 = test_stub.create_multi_vms(name_prefix='vm3', count=1,
                                     ps_uuid=ps2.uuid, data_volume_number=VOLUME_NUMBER,
                                     ps_uuid_for_data_vol=ps2.uuid)[0]
    vm4 = test_stub.create_multi_vms(name_prefix='vm4', count=1,
                                     ps_uuid=ps2.uuid, data_volume_number=VOLUME_NUMBER,
                                     ps_uuid_for_data_vol=ps1.uuid)[0]
    vm_list = [vm1, vm2, vm3, vm4]

    for vm in vm_list:
        test_obj_dict.add_vm(vm)

    ps_ops.change_primary_storage_state(state='maintain', primary_storage_uuid=ps2.uuid)
    maintenance_ps_list.append(ps2)
    time.sleep(60)

    vr_vm_list = test_lib.lib_find_vr_by_vm(vm1.get_vm())
    vr_vm = None
    if vr_vm_list:
        vr_vm = vr_vm_list[0]
        if vr_vm.allVolumes[0].primaryStorageUuid == ps2.uuid:
            assert vr_vm.state == inventory.STOPPED
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
        with test_stub.expect_failure("start vm in maintenance ps", Exception):
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