'''
Test sync after adding disk to vm in vmware

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

def test():
    global vm
    volumes = []

    ova_image_name = os.environ['vcenterDefaultmplate']
    network_pattern = 'L3-%s'%os.environ['dportgroup']
    if not vct_ops.lib_get_vcenter_l3_by_name(network_pattern):
        network_pattern = 'L3-%s'%os.environ['portgroup0']
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    #create vm
    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm_1', image_name = ova_image_name, l3_name = network_pattern)
    vm.check()

    vcenter = os.environ.get('vcenter')
    SI = vct_ops.connect_vcenter(vcenter)
    content = SI.RetrieveContent()
    vm = vct_ops.get_vm(content, name = 'vm_1')[0]
    #add 2 disks to vcenter vm
    disk1 = vct_ops.add_disk(vm, 2)
    disk2 = vct_ops.add_disk(vm, 5)
    disk_file = vct_ops.get_data_volume_attach_to_vm(vm)
    #sync vcenter
    vcenter_uuid = vct_ops.lib_get_vcenter_by_name(vcenter).uuid
    vct_ops.sync_vcenter(vcenter_uuid)
    time.sleep(5)

    allvolumes = vct_ops.lib_get_vm_by_name('vm_1').allVolumes
    assert len(allvolumes) == 3
    for volume in allvolumes:
        if volume.type == 'Data':
            volumes.append(volume.installPath)
    assert set(volumes) ^ set(disk_file) == set([])

    #cleanup
    vct_ops.destroy_vm(vm)
    vct_ops.sync_vcenter(vcenter_uuid)

    test_util.test_pass("sync after adding disk to vm in vmware test passed.")


def error_cleanup():
    global vm
    if vm:
        vct_ops.destroy_vm(vm)