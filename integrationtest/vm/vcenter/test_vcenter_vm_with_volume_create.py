'''
test for creating vm with volume in vcenter
@author: tianye
'''


import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import test_stub
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    global test_obj_dict

    ova_image_name = os.environ['vcenterDefaultmplate']
    centos_image_name = os.environ['image_dhcp_name'] 
    network_pattern1 = os.environ['l3vCenterNoVlanNetworkName']
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    #create vm with disk
    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm-create-with-disk', image_name = centos_image_name, l3_name = network_pattern1, disk_offering_uuids = [disk_offering.uuid] )
    vm.check()
    vm.destroy()
    vm.check()
    vm.expunge()
    #create vm1 without disk
    vm1 = test_stub.create_vm_in_vcenter(vm_name = 'test_vcenter_vm1', image_name = ova_image_name, l3_name = network_pattern1)
    test_obj_dict.add_vm(vm1)
    
    test_util.test_dsc('Create volume and check')
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_name('vcenter3_volume')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()

    test_util.test_dsc('Attach volume and check')
    #mv vm checker later, to save some time.
    vm1.check()
    volume.attach(vm1)
    volume.check()

    test_util.test_dsc('Detach volume and check')
    volume.detach()
    volume.check()
 
    test_util.test_dsc('Attach volume which was detached and check')
    volume.attach(vm1)
    volume.check()

    test_util.test_dsc('Delete volume which was attached to vm and check')
    volume.delete()
    volume.check()
    test_obj_dict.rm_volume(volume)

    test_util.test_dsc('Recover volume and check')
    volume.recover()
    volume.check()
    test_obj_dict.add_volume(volume)

    test_util.test_dsc('Attach volume, detach volume, then delete volume and check')
    volume.attach(vm1)
    volume.check()
    volume.detach()
    volume.check()
    volume.delete()
    volume.check()
    test_obj_dict.rm_volume(volume)

    volume.recover()
    volume.check()
    test_obj_dict.add_volume(volume)
    test_util.test_dsc('Expunge vm , then test volume can be expunged or not')
    volume.attach(vm1)
    volume.check()
    vm1.destroy()
    vm1.expunge()
    volume.delete()
    volume.check()
    volume.expunge()
    volume.check()
    test_obj_dict.rm_volume(volume)
    
    test_util.test_pass("Creating vm with disk volume of vcenter test passed.")


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
