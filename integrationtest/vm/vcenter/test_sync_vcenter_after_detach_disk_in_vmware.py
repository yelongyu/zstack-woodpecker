'''
Test sync after detach disk from vm in vmware

@author: guocan
'''
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import test_stub

import os
import time

test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    volumes = []

    ova_image_name = os.environ['vcenterDefaultmplate']
    network_pattern = 'L3-%s'%os.environ['dportgroup']
    if not vct_ops.lib_get_vcenter_l3_by_name(network_pattern):
        network_pattern = 'L3-%s'%os.environ['portgroup0']
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    #create vm with disk
    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm_2', image_name = ova_image_name, l3_name = network_pattern, disk_offering_uuids = [disk_offering.uuid, disk_offering.uuid] )
    test_obj_dict.add_vm(vm)
    vm.check()

    vcenter = os.environ.get('vcenter')
    SI = vct_ops.connect_vcenter(vcenter)
    content = SI.RetrieveContent()
    vm = vct_ops.get_vm(content, name = 'vm_2')[0]
    
    vct_ops.delete_virtual_disk(vm, 2)
    vct_ops.delete_virtual_disk(vm, 2)
    vcenter_uuid = vct_ops.lib_get_vcenter_by_name(vcenter).uuid
    vct_ops.sync_vcenter(vcenter_uuid)
    time.sleep(5)
    allvolumes = vct_ops.lib_get_vm_by_name('vm_2').allVolumes
    assert len(allvolumes) == 1
    for volume in allvolumes:
        if volume.type == 'Data':
            volumes.append(volume.installPath)
    assert set(volumes) == set([])

    #cleanup
    test_lib.lib_error_cleanup(test_obj_dict)

    test_util.test_pass("sync after detaching disk from vm in vmware test passed.")


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
   