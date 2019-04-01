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

case_flavor = dict(other_ps_volume = dict(with_vm=True, detach=False),
                   all_ps_volume   = dict(with_vm=False, detach=True)
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
        multi_ps.create_data_volume(except_ps_type='SharedBlock')
        multi_ps.create_vm(except_ps_type='SharedBlock')
        multi_ps.create_data_volume(shared=True, ps_type='SharedBlock')

    vm = multi_ps.vm[0]
    vm.stop()
    vm.reinit()
    if flavor['detach']:
        for volume in multi_ps.data_volume.values():
            volume.detach(vm.get_vm().uuid)
    vm.start()
    vm.check()

    test_util.test_pass('SAN VM Reimage Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if multi_ps.vm:
        try:
            for vm in multi_ps.vm:
                vm.destroy()
        except:
            pass
