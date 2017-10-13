'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.operations.vm_operations as vm_ops


_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

DISABLED = 'Disabled'
ENABLE = 'Enabled'
MAINTAIMANCE = 'Maintain'

case_flavor = dict(local_disabled=      dict(local_state=DISABLED, shared_state=ENABLE),
                   shared_disabled=     dict(local_state=ENABLE, shared_state=DISABLED),
                   local_maintain=      dict(local_state=MAINTAIMANCE, shared_state=ENABLE),
                   shared_maintain=     dict(local_state=ENABLE, shared_state=MAINTAIMANCE),
                   )


@test_stub.skip_if_not_local_shared
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    ps_env = test_stub.PSEnvChecker()
    local_ps, shared_ps = ps_env.get_two_ps()
    if flavor['local_state'] is DISABLED:
        ps_ops.change_primary_storage_state(local_ps.uuid, state='disable')
    elif flavor['local_state'] is MAINTAIMANCE:
        ps_ops.change_primary_storage_state(local_ps.uuid, state='maintain')

    if flavor['shared_state'] is DISABLED:
        ps_ops.change_primary_storage_state(shared_ps.uuid, state='disable')
    elif flavor['shared_state'] is MAINTAIMANCE:
        ps_ops.change_primary_storage_state(shared_ps.uuid, state='maintain')

    if flavor['local_state'] in (DISABLED, MAINTAIMANCE):
        with test_lib.expected_failure('Create vm in ps in {} or {} state'.format(DISABLED,MAINTAIMANCE), Exception):
            test_stub.create_multi_vms(name_prefix='test-vm', count=1, ps_uuid=local_ps.uuid)

    if flavor['local_state'] is DISABLED:
        vm1 = test_stub.create_multi_vms(name_prefix='test-vm', count=1, ps_uuid=shared_ps.uuid)[0]
        test_obj_dict.add_vm(vm1)
        vm2 = test_stub.create_multi_vms(name_prefix='test-vm', count=1, ps_uuid=shared_ps.uuid,
                                         data_volume_number=1, ps_uuid_for_data_vol=shared_ps.uuid)[0]
        test_obj_dict.add_vm(vm2)

    if flavor['shared_state'] in (DISABLED, MAINTAIMANCE):
        with test_lib.expected_failure('Create vm in ps in {} or {} state'.format(DISABLED,MAINTAIMANCE), Exception):
            test_stub.create_multi_vms(name_prefix='test-vm', count=1, ps_uuid=shared_ps.uuid)

        vm1 = test_stub.create_multi_vms(name_prefix='test-vm', count=1, ps_uuid=local_ps.uuid)[0]
        test_obj_dict.add_vm(vm1)
        vm2 = test_stub.create_multi_vms(name_prefix='test-vm', count=1, ps_uuid=local_ps.uuid,
                                         data_volume_number=1, ps_uuid_for_data_vol=local_ps.uuid)[0]
        test_obj_dict.add_vm(vm2)

    if flavor['local_state'] in (DISABLED, MAINTAIMANCE):
        ps_ops.change_primary_storage_state(local_ps.uuid, state='enable')
    if flavor['shared_state'] in (DISABLED, MAINTAIMANCE):
        ps_ops.change_primary_storage_state(shared_ps.uuid, state='enable')

    test_lib.lib_error_cleanup(test_obj_dict)


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
