'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import apibinding.inventory as inventory
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

DISABLED = 'Disabled'
ENABLE = 'Enabled'
MAINTENANCE = 'Maintenance'

case_flavor = dict(both_disabled =      dict(local_state=DISABLED, shared_state=DISABLED, reconnect=False, vm_ha=True),
                   local_maintain=      dict(local_state=MAINTENANCE, shared_state=ENABLE, reconnect=False, vm_ha=True),
                   shared_maintain=     dict(local_state=ENABLE, shared_state=MAINTENANCE, reconnect=False, vm_ha=False),
                   both_reconnect =     dict(local_state=ENABLE, shared_state=ENABLE, reconnect=True, vm_ha=False),
                   )


@test_stub.skip_if_not_local_shared
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    ps_env = test_stub.PSEnvChecker()
    local_ps, shared_ps = ps_env.get_two_ps()

    vm_list=list(test_stub.generate_local_shared_test_vms(test_obj_dict, vm_ha=flavor['vm_ha']))
    (vm_root_local, vm_root_local_data_local,
     vm_root_local_data_shared, vm_root_local_data_mixed,
     vm_root_shared, vm_root_shared_data_local,
     vm_root_shared_data_shared, vm_root_shared_data_mixed) = vm_list

    if flavor['local_state'] is DISABLED:
        ps_ops.change_primary_storage_state(local_ps.uuid, state='disable')
        time.sleep(10)
        for vm in vm_list:
            vm.update()
            assert vm.get_vm().state == inventory.RUNNING

    if flavor['shared_state'] is DISABLED:
        ps_ops.change_primary_storage_state(shared_ps.uuid, state='disable')
        time.sleep(10)
        for vm in vm_list:
            vm.update()
            assert vm.get_vm().state == inventory.RUNNING

    if flavor['reconnect']:
        for ps in (local_ps, shared_ps):
            ps_ops.reconnect_primary_storage(ps.uuid)
        for vm in vm_list:
            vm.update()
            assert vm.get_vm().state == inventory.RUNNING

    if flavor['local_state'] is MAINTENANCE:
        ps_ops.change_primary_storage_state(local_ps.uuid, state='maintain')
        maintain_ps = local_ps
    if flavor['shared_state'] is MAINTENANCE:
        ps_ops.change_primary_storage_state(shared_ps.uuid, state='maintain')
        maintain_ps = shared_ps
    time.sleep(60)

    if MAINTENANCE in (flavor['local_state'], flavor['shared_state']):
        vr_vm_list = test_lib.lib_find_vr_by_vm(vm_list[0].get_vm())
        vr_vm = None
        if vr_vm_list:
            vr_vm = vr_vm_list[0]
            if vr_vm.allVolumes[0].primaryStorageUuid == maintain_ps.uuid:
                assert vr_vm.state == inventory.STOPPED
            else:
                assert vr_vm.state == inventory.RUNNING

        for vm in vm_list:
            vm.update()

    if flavor['local_state'] is MAINTENANCE:
        for vm in (vm_root_local, vm_root_local_data_local,vm_root_local_data_shared, vm_root_local_data_mixed,
                   vm_root_shared_data_mixed,vm_root_shared_data_local):
            vm.update()
            assert vm.get_vm().state == inventory.STOPPED
            with test_stub.expected_failure("start vm in maintenance ps", Exception):
                vm.start()

        for vm in (vm_root_shared, vm_root_shared_data_shared):
            vm.update()
            assert vm.get_vm().state == inventory.RUNNING

    if flavor['shared_state'] is MAINTENANCE:
        for vm in (vm_root_shared, vm_root_shared_data_shared,vm_root_shared_data_local, vm_root_shared_data_mixed,
                   vm_root_local_data_mixed,vm_root_local_data_shared):
            vm.update()
            assert vm.get_vm().state == inventory.STOPPED
            with test_stub.expected_failure("start vm in maintenance ps", Exception):
                vm.start()
        for vm in (vm_root_local, vm_root_local_data_local):
            vm.update()
            assert vm.get_vm().state == inventory.RUNNING

    if flavor['local_state'] is MAINTENANCE:
        ps_ops.change_primary_storage_state(local_ps.uuid, state='enable')
    if flavor['shared_state'] is MAINTENANCE:
        ps_ops.change_primary_storage_state(shared_ps.uuid, state='enable')

#    if MAINTENANCE in (flavor['local_state'], flavor['shared_state']):
#        if vr_vm and vr_vm.state == inventory.STOPPED:
#            vm_ops.start_vm(vr_vm.uuid)

    for vm in vm_list:
        vm.update()
        if vm.get_vm().state == inventory.STOPPED and vm.get_vm().type != 'ApplianceVm':
            vm.start()
        vm.check()



def env_recover():
    local_ps, shared_ps = test_stub.PSEnvChecker().get_two_ps()
    if local_ps.state in ('Disabled', "Maintenance"):
        ps_ops.change_primary_storage_state(local_ps.uuid, state='enable')
    if shared_ps.state in ('Disabled', "Maintenance"):
        ps_ops.change_primary_storage_state(shared_ps.uuid, state='enable')
    for vr in res_ops.get_resource(res_ops.APPLIANCE_VM):
        if vr.state != inventory.RUNNING:
            vm_ops.start_vm(vr.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
