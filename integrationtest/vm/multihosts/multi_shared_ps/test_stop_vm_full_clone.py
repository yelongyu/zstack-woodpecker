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

case_flavor = dict(shared_vm_ceph_volume = dict(shared_vm=True, one_volume=True, shared_volume=False),
                   shared_vm_2volume = dict(shared_vm=True, one_volume=False),
                   ceph_vm_shared_volume = dict(shared_vm=False, one_volume=True, shared_volume=True),
                   ceph_vm_2volume = dict(shared_vm=False, one_volume=False)
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
    if flavor['one_volume']:
        if flavor['shared_volume']:
            multi_ps.create_data_volume(vms=multi_ps.vm, ps_type='SharedBlock')
        else:
            multi_ps.create_data_volume(vms= multi_ps.vm, ps_type='Ceph')
    else:
        multi_ps.create_data_volume(vms=multi_ps.vm, ps_type='SharedBlock')
        multi_ps.create_data_volume(vms= multi_ps.vm, ps_type='Ceph')

    vm = multi_ps.vm[0]
    vm.stop()
    cloned_vm = vm.clone(['test_stop_vm_full_clone'], full=True)[0]
    multi_ps.vm.append(cloned_vm)

    volumes_number = len(test_lib.lib_get_all_volumes(cloned_vm))
    if flavor['one_volume']:
        if volumes_number != 2:
            test_util.test_fail('Did not just find 2 volumes for [vm:] %s. But we assigned 1 data volume to the vm. We only catch %s volumes' % (cloned_vm.uuid, volumes_number))
        else:
            test_util.test_logger('Find 2 volumes for [vm:] %s.' % cloned_vm.uuid)
    else:
        if volumes_number != 3:
            test_util.test_fail('Did not just find 3 volumes for [vm:] %s. But we assigned 2 data volume to the vm. We only catch %s volumes' % (cloned_vm.uuid, volumes_number))
        else:
            test_util.test_logger('Find 3 volumes for [vm:] %s.' % cloned_vm.uuid)    
    
    test_util.test_pass('Full Clone Stopped VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if multi_ps.vm:
        try:
            for vm in multi_ps.vm:
                vm.destroy()
        except:
            pass
