'''
New Integration Test for cloning KVM VM.
Behavior check: cloned vm should not have data volume.

@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vn_prefix = 'vm-clone-%s' % time.time()
vm_names = ['%s-vm1' % vn_prefix]

def test():
    vm = test_stub.create_vm(vm_name = vn_prefix)
    test_obj_dict.add_vm(vm)

    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    #volume_creation_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi'])
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume.attach(vm)

    new_vms = vm.clone(vm_names)
    for new_vm in new_vms:
        test_obj_dict.add_vm(new_vm)

    if len(new_vms) != len(vm_names):
        test_util.test_fail('only %s VMs have been cloned, which is less than required: %s' % (len(new_vms), vm_names))

    for new_vm in new_vms:
        new_vm = new_vm.get_vm()
        try:
            vm_names.remove(new_vm.name)
            test_util.test_logger('VM:%s name: %s is found' % (new_vm.uuid, new_vm.name))
        except:
            test_util.test_fail('%s vm name: %s is not in list: %s' % (new_vm.uuid, new_vm.name, vm_names))
    
    if test_lib.lib_get_data_volumes(new_vms[0]) != []:
        test_util.test_fail('The cloned vm is still have data volume, the expected behavior is only clone root volume.')
    

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Clone VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
