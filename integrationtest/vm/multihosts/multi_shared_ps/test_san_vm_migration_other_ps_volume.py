'''

New Integration Test for multiple shared primary storage

@author: Legion
'''

import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
multi_ps = test_stub.MultiSharedPS()

case_flavor = dict(volume_created_with_vm = dict(with_vm=True, shared=False, ps2_vm=False),
                   volume_single_created = dict(with_vm=False, shared=False, ps2_vm=False),
                   shared_volume = dict(with_vm=False, shared=True, ps2_vm=False),
                   shared_volume_2ps_vm = dict(with_vm=False, shared=True, ps2_vm=True)
                   )

def test():
    ps_inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    sblk_ps = [ps for ps in ps_inv if ps.type == 'SharedBlock']
    if not sblk_ps:
        test_util.test_skip('Skip test as there is not SharedBlock primary storage')
    flavor = case_flavor[os.getenv('CASE_FLAVOR')]
    if flavor['with_vm']:
        multi_ps.create_vm(ps_type='SharedBlock', with_data_vol=True, one_volume=True)
    else:
        multi_ps.create_vm(ps_type='SharedBlock')
    if flavor['shared']:
        if flavor['ps2_vm']:
            multi_ps.create_vm(except_ps_type='SharedBlock')
        else:
            multi_ps.create_vm(ps_type='SharedBlock')
        multi_ps.create_data_volume(shared=True, vms=multi_ps.vm, except_ps_type='SharedBlock')
    else:
        if not flavor['with_vm']:
            multi_ps.create_data_volume(vms=multi_ps.vm, except_ps_type='SharedBlock')

    if flavor['shared']:
        for data_volume in multi_ps.data_volume.values():
            for vm in multi_ps.vm:
                data_volume.detach(vm.get_vm().uuid)
        if flavor['ps2_vm']:
            multi_ps.migrate_vm()
        else:
            multi_ps.migrate_vm(multi_ps.vm)
        for data_volume in multi_ps.data_volume.values():
            for vm in multi_ps.vm:
                data_volume.attach(vm)
    else:
        multi_ps.migrate_vm()

    test_util.test_pass('SAN VM PS Migration with other PS Volume Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if multi_ps.vm:
        try:
            for vm in multi_ps.vm:
                vm.destroy()
        except:
            pass
