'''

New Integration Test for multiple shared primary storage in one cluster

@author: Forat
'''

import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
multi_ps = test_stub.MultiSharedPS()

case_flavor = dict(ceph_vm_ceph_bs = dict(shared_vm=False, imagestore_bs=False),
                   ceph_vm_imagestore_bs = dict(shared_vm=False, imagestore_bs=True),
                   shared_vm_imagestore_bs = dict(shared_vm=True, imagestore_bs=True)
                   )

def test():
    ps_inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    ceph_ps = [ps for ps in ps_inv if ps.type == 'Ceph']
    if not ceph_ps:
        test_util.test_skip('Skip test as there is not Ceph primary storage')
    
    flavor = case_flavor[os.getenv('CASE_FLAVOR')]
    
    if flavor['shared_vm']:
        multi_ps.create_vm(image_name="ttylinux", ps_type="SharedBlock")
    else:
        multi_ps.create_vm(image_name="ttylinux", ps_type="Ceph")
    multi_ps.create_data_volume(vms=multi_ps.vm, ps_type='SharedBlock')
    multi_ps.create_data_volume(vms= multi_ps.vm, ps_type='Ceph')

    vm = multi_ps.vm[0]
    last_data_volumes_uuids = []
    last_data_volumes = test_lib.lib_get_data_volumes(vm.get_vm())
    for data_volume in last_data_volumes:
        last_data_volumes_uuids.append(data_volume.uuid)
    last_l3network_uuid = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
    last_primarystorage_uuid = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
    vm.stop()

    if flavor['imagestore_bs']:
        image_uuid = test_lib.lib_get_image_by_name("image_for_sg_test", bs_type="ImageStoreBackupStorage").uuid
    else:
        image_uuid = test_lib.lib_get_image_by_name("image_for_sg_test", bs_type="Ceph").uuid
    vm_ops.change_vm_image(vm.get_vm().uuid, image_uuid)
    vm.start()
    vm.update()

    #check whether the vm is running successfully
    if not test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, 22, 1200):
        test_util.test_fail('VM:%s is not startup in 1200 seconds.' % vm.get_vm().uuid)
    #check whether data volumes attached to the vm has changed
    now_data_volumes_uuids = []
    now_data_volumes = test_lib.lib_get_data_volumes(vm.get_vm())
    for data_volume in now_data_volumes:
        now_data_volumes_uuids.append(data_volume.uuid)
    if set(last_data_volumes_uuids) != set(now_data_volumes_uuids):
        test_util.test_fail('Change Vm Image Failed.Data volumes changed.')
    #check whether the network config has changed
    now_l3network_uuid = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
    if now_l3network_uuid != last_l3network_uuid:
        test_util.test_fail('Change VM Image Failed.The Network config has changed.')
    #check whether primarystorage has changed
    now_primarystorage_uuid = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
    if now_primarystorage_uuid != last_primarystorage_uuid:
        test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')

    test_util.test_pass('Change Vm Image Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if multi_ps.vm:
        try:
            for vm in multi_ps.vm:
                vm.destroy()
        except:
            pass
