'''
test for creating vm with volume in vcenter
@author: tianye
'''


import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import test_stub
import os

import zstackwoodpecker.header.header as zstack_header
import zstackwoodpecker.header.volume as volume_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.image as image_header


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


vm = None

def test():
    global vm
    global vm1
    global volume

    ova_image_name = os.environ['vcenterDefaultmplate']
    centos_image_name = os.environ['image_dhcp_name']
    #network_pattern1 = os.environ['vcenterDefaultNetwork']
    network_pattern1 = os.environ['l3vCenterNoVlanNetworkName']
    #disk_offering1 = os.environ['largeDiskOfferingName']  
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))

    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm-create-with-disk', image_name = centos_image_name, l3_name = network_pattern1, disk_offering_uuids = [disk_offering.uuid] )
    vm.check()

    vm.destroy()
    vm.check()
    vm.expunge()
   # create vm1 without disk, and create volume and attach to vm1,detach from vm1, delete volume 
    vm1 = test_stub.create_vm_in_vcenter(vm_name = 'test_vcenter_vm1', image_name = ova_image_name, l3_name = network_pattern1)
    
    test_obj_dict.add_vm(vm1)

    test_util.test_dsc('Create volme and check')
    disk_offering1 = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering1.uuid)
    volume_creation_option.set_name('vcenter3_volume')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    #volume.check()

    test_util.test_dsc('Attach volume and check')
    #mv vm checker later, to save some time.
    vm1.check()
    volume.attach(vm1)
    #volume.check()

    test_util.test_dsc('Detach volume and check')
    volume.detach()
    #volume.check()

    test_util.test_dsc('Delete volume and check')
    volume.delete()
    #volume.check()
    test_obj_dict.rm_volume(volume)

    vm1.destroy()
    vm1.check()

    test_util.test_pass("Creating vm with disk volume of vcenter test passed.")



def error_cleanup():
    global vm
    if vm:
        vm.destroy()
        vm.expunge()
