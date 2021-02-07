'''
Test for deleting and expunge iso cloned vm ops.

The key step:
-add iso
-create vm1 from iso
-clone vm2 from vm1
-del iso
-resize vm2 root volume
-expunge and detach iso
-change vm2 state

@author: PxChen
'''

import os
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
iso = None

def test():
    global iso
    global test_obj_dict

    # run condition
    allow_bs_list = [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE, inventory.CEPH_BACKUP_STORAGE_TYPE]
    test_lib.skip_test_when_bs_type_not_in_list(allow_bs_list)

    hosts = res_ops.query_resource(res_ops.HOST)
    if len(hosts) <= 1:
        test_util.test_skip("skip for host_num is not satisfy condition host_num>1")

    # add iso and create vm from iso
    iso = test_stub.add_test_minimal_iso('minimal_iso')
    test_obj_dict.add_image(iso)
    root_volume_offering = test_stub.add_test_root_volume_offering('root-disk-iso', 10737418240)
    test_obj_dict.add_disk_offering(root_volume_offering)
    vm_offering = test_stub.add_test_vm_offering(2, 1024*1024*1024, 'iso-vm-offering')
    test_obj_dict.add_instance_offering(vm_offering)
    vm = test_stub.create_vm_with_iso_for_test(vm_offering.uuid, iso.image.uuid, root_volume_offering.uuid, 'iso-vm')
    test_obj_dict.add_vm(vm)

    # check vm
    vm_inv = vm.get_vm()
    test_lib.lib_set_vm_host_l2_ip(vm_inv)
    test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, 22, 1800)

    # clone vm
    cloned_vm_name = ['cloned_vm']
    cloned_vm_obj = vm.clone(cloned_vm_name)[0]
    test_obj_dict.add_vm(cloned_vm_obj)

    # delete iso
    iso.delete()

    # vm ops test
    test_stub.vm_ops_test(cloned_vm_obj, "VM_TEST_RESIZE_RVOL")

    # expunge iso
    iso.expunge()

    #detach iso
    img_ops.detach_iso(vm.vm.uuid)

    # vm ops test
    test_stub.vm_ops_test(cloned_vm_obj, "VM_TEST_STATE")

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Cloned VM ops for BS Success')

# Will be called only if exception happens in test().
def error_cleanup():
    global iso
    global test_obj_dict

    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        iso.delete()
    except:
        pass
