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

case_flavor = dict(volume_created_with_vm = dict(with_vm=True, root_sp=True),
                   volume_single_created = dict(with_vm=False, root_sp=False)
                   )

def test():
    ps_inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    ceph_ps = [ps for ps in ps_inv if ps.type == 'Ceph']
    if not ceph_ps:
        test_util.test_skip('Skip test as there is not Ceph primary storage')
    flavor = case_flavor[os.getenv('CASE_FLAVOR')]
    if flavor['with_vm']:
        multi_ps.create_vm(ceph_image=True, with_data_vol=True, one_volume=True)
    else:
        multi_ps.create_vm(ceph_image=True, set_ps_uuid=False)
    multi_ps.create_data_volume(vms=multi_ps.vm, except_ps_type='Ceph')
    if flavor['root_sp']:
        for vm in multi_ps.vm:
            multi_ps.create_snapshot(vm=vm)
    else:
        multi_ps.create_snapshot(data_volume=multi_ps.data_volume)
    for vol_uuid in multi_ps.snapshot.keys():
        multi_ps.revert_sp(vol_uuid)
        multi_ps.create_snapshot(vol_uuid=vol_uuid)
        multi_ps.create_snapshot(vol_uuid=vol_uuid)

    for vol_uuid in multi_ps.snapshot.keys():
        multi_ps.revert_sp(vol_uuid)
        multi_ps.delete_snapshot(vol_uuid)

    test_util.test_pass('Ceph VM with other PS Volume Snapshot Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if multi_ps.vm:
        try:
            for vm in multi_ps.vm:
                vm.destroy()
        except:
            pass
