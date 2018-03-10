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

vm = None

def test():
    global vm

    #ova_image_name = os.environ['vcenterDefaultmplate']
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

    test_util.test_pass("Creating vm with disk volume of vcenter test passed.")



def error_cleanup():
    global vm
    if vm:
        vm.destroy()
        vm.expunge()
