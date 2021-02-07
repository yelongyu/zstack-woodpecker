'''
test for detached vcenter volume
@author: guocan
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import test_stub
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    global test_obj_dict

    ova_image_name = os.environ['vcenterDefaultmplate']
    network_pattern1 = 'L3-%s'%os.environ['dportgroup']
    if not vct_ops.lib_get_vcenter_l3_by_name(network_pattern1):
        network_pattern1 = 'L3-%s'%os.environ['portgroup0']
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))

    #create vm with disk
    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm_with_disk', image_name = ova_image_name, l3_name = network_pattern1, disk_offering_uuids = [disk_offering.uuid])
    test_obj_dict.add_vm(vm)
    vm.check()
   
    #create vm1 without disk
    vm1 = test_stub.create_vm_in_vcenter(vm_name = 'test_detached_volume_vm', image_name = ova_image_name, l3_name = network_pattern1)
    test_obj_dict.add_vm(vm1)
    vm1.check()
    
    test_util.test_dsc('Create 2 volumes')
    disk_offering1 = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering1.uuid)
    volume_creation_option.set_name('vcenter_datavolume')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume_creation_option.set_name('vcenter_datavolume1')
    volume1 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume1)
    volume1.check()

    test_util.test_dsc('Attach volume to vm, volume1 to vm1')
    #mv vm checker later, to save some time.
    volume.attach(vm)
    volume.check()
    volume1.attach(vm1)
    volume1.check()

    test_util.test_dsc('Detach volume1 and attach it to vm')
    volume1.detach()
    volume1.check()
    volume1.attach(vm)
    volume1.check()
 
    test_util.test_dsc('Destroy vm and attach volume to vm1')
    vm.destroy()
    volume.attach(vm1)
    volume.check()
    test_util.test_dsc('Expunge vm and attach volume1 to vm1')
    vm.expunge()
    test_obj_dict.rm_vm(vm)
    volume1.attach(vm1)
    volume1.check()

    volume.detach()
    volume.check()
    volume1.delete()
    volume1.check()
    test_obj_dict.rm_volume(volume1)
    
    #cleanup
    test_lib.lib_error_cleanup(test_obj_dict)

    test_util.test_pass("Test for detached vcenter volume passed.")


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
