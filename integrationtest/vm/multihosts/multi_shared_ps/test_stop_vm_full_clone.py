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

case_flavor = dict(shared_vm_to_shared_vm_ceph_volume = dict(shared_vm=True, to_shared_vm=True, to_shared_volume=False),
                   shared_vm_to_ceph_vm_shared_volume = dict(shared_vm=True, to_shared_vm=False, to_shared_volume=True),
                   ceph_vm_to_shared_vm_ceph_volume = dict(shared_vm=False, to_shared_vm=True, to_shared_volume=False),
                   ceph_vm_to_ceph_vm_shared_volume = dict(shared_vm=False, to_shared_vm=False, to_shared_volume=True)
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
    multi_ps.create_data_volume(vms=multi_ps.vm, ps_type='SharedBlock')
    multi_ps.create_data_volume(vms= multi_ps.vm, ps_type='Ceph')

    vm = multi_ps.vm[0]
    vm.stop()

    shared_ps = multi_ps.get_ps(ps_type='SharedBlock')
    ceph_ps = multi_ps.get_ps(ps_type='Ceph')
    if flavor['to_shared_vm']:
        if not flavor['to_shared_volume']:
            ps_uuid_for_root_volume = shared_ps.uuid
            ps_uuid_for_data_volume = ceph_ps.uuid
    else:
        if flavor['to_shared_volume']:
            ps_uuid_for_root_volume = ceph_ps.uuid
            ps_uuid_for_data_volume = shared_ps.uuid
    root_volume_systag = []
    data_volume_systag = ["volumeProvisioningStrategy::ThinProvisioning"]
    cloned_vm = vm.clone(['test_stop_vm_full_clone'], full=True, ps_uuid_for_root_volume=ps_uuid_for_root_volume, ps_uuid_for_data_volume=ps_uuid_for_data_volume, root_volume_systag=root_volume_systag, data_volume_systag=data_volume_systag)[0]
    multi_ps.vm.append(cloned_vm.vm)

    volumes_list = test_lib.lib_get_all_volumes(cloned_vm.vm)
    volumes_number = len(volumes_list)
    if volumes_number != 3:
        test_util.test_fail('Did not just find 3 volumes for [vm:] %s. But we assigned 2 data volume to the vm. We only catch %s volumes' % (cloned_vm.vm.uuid, volumes_number))
    else:
        test_util.test_logger('Find 3 volumes for [vm:] %s.' % cloned_vm.vm.uuid)
        ps = test_lib.lib_get_primary_storage_by_uuid(test_lib.lib_get_root_volume(cloned_vm.vm).primaryStorageUuid)
        data_volume_ps1 = test_lib.lib_get_primary_storage_by_uuid(test_lib.lib_get_data_volumes(cloned_vm.vm)[0].primaryStorageUuid)
        data_volume_ps2 = test_lib.lib_get_primary_storage_by_uuid(test_lib.lib_get_data_volumes(cloned_vm.vm)[1].primaryStorageUuid)
        if flavor['to_shared_vm']:
            if not flavor['to_shared_volume']:
                test_util.test_logger(ps.type + data_volume_ps1.type + data_volume_ps2.type)
                assert ps.type == 'SharedBlock' and data_volume_ps1.type == 'Ceph' and data_volume_ps2.type == 'Ceph'
        else:
            if flavor['to_shared_volume']:
                test_util.test_logger(ps.type + data_volume_ps1.type + data_volume_ps2.type)
                assert ps.type == 'Ceph' and data_volume_ps1.type == 'SharedBlock' and data_volume_ps2.type == 'SharedBlock'
    
    test_util.test_pass('Full Clone Stopped VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if multi_ps.vm:
        try:
            for vm in multi_ps.vm:
                vm.destroy()
        except:
            pass
