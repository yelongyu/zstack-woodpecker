'''

New Integration Test for multiple shared primary storage in one cluster

@author: Forat
'''

import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
multi_ps = test_stub.MultiSharedPS()

case_flavor = dict(running_shared_vm_to_ceph_vm = dict(shared_vm=True, running=True, to_shared_vm=False),
                   stopped_shared_vm_to_ceph_vm = dict(shared_vm=True, running=False, to_shared_vm=False),
                   running_ceph_vm_to_shared_vm = dict(shared_vm=False, running=True, to_shared_vm=True),
                   stopped_ceph_vm_to_shared_vm = dict(shared_vm=False, running=False, to_shared_vm=True)
                   )

def test():
    ps_inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    ceph_ps = [ps for ps in ps_inv if ps.type == 'Ceph']
    if not ceph_ps:
        test_util.test_skip('Skip test as there is not Ceph primary storage')
    
    flavor = case_flavor[os.getenv('CASE_FLAVOR')]
    
    if flavor['shared_vm']:
        multi_ps.create_vm(ps_type="SharedBlock")
    else:
        multi_ps.create_vm(ps_type="Ceph")
    vm = multi_ps.vm[0]
    if not flavor['running']:
        vm.stop()
    
    shared_ps = multi_ps.get_ps(ps_type='SharedBlock')
    ceph_ps = multi_ps.get_ps(ps_type='Ceph')
    if flavor['to_shared_vm']:
        ps_uuid_for_root_volume = shared_ps.uuid
    else:
        ps_uuid_for_root_volume = ceph_ps.uuid
    root_volume_systag = []
    cloned_vm = vm.clone(['test_stop_vm_full_clone'], full=True, ps_uuid_for_root_volume=ps_uuid_for_root_volume, root_volume_systag=root_volume_systag)[0]
    multi_ps.vm.append(cloned_vm.vm)

    volumes_list = test_lib.lib_get_all_volumes(cloned_vm.vm)
    volumes_number = len(volumes_list)
    if volumes_number != 1:
        test_util.test_fail('Did not just find 1 volumes for [vm:] %s.' % cloned_vm.vm.uuid)
    else:
        test_util.test_logger('Find 1 volumes for [vm:] %s.' % cloned_vm.vm.uuid)
        ps = test_lib.lib_get_primary_storage_by_uuid(test_lib.lib_get_root_volume(cloned_vm.vm).primaryStorageUuid)
        if flavor['to_shared_vm']:
            assert ps.type == 'SharedBlock' 
        else:
            assert ps.type == 'Ceph'

    test_util.test_pass('VM Clone Without Volume Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if multi_ps.vm:
        try:
            for vm in multi_ps.vm:
                vm.destroy()
        except:
            pass
