'''
test data volume's status after sync vcenter
@author: guocan
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import test_stub

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict

    ova_image_name = os.environ['vcenterDefaultmplate']
    network_pattern1 = os.environ['l3vCenterNoVlanNetworkName']
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    test_util.test_dsc('Create vm and check')
    vm = test_stub.create_vm_in_vcenter(vm_name = 'test_volume_after_sync_vm', image_name = ova_image_name, l3_name = network_pattern1)
    test_obj_dict.add_vm(vm)
    vm.check()
    ps_uuid = vm.vm.allVolumes[0].primaryStorageUuid
    vc_ps = test_lib.lib_get_primary_storage_by_uuid(ps_uuid)
    vc_host = test_lib.lib_find_host_by_vm(vm.vm).managementIp

    test_util.test_dsc('Create volumes and check')
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_name('vcenter_volume')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume.attach(vm)
    volume.check()
    volume.detach()
    volume.check()

    volume_creation_option.set_name('vcenter_volume1')
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    volume1 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume1)
    volume1.check()
    volume1.attach(vm) 
    volume1.check()
    volume1.delete()
    volume1.check()

    test_util.test_dsc('Sync vcenter')
    vcenter_uuid = vct_ops.lib_get_vcenter_by_name(os.environ['vcenter']).uuid
    vct_ops.sync_vcenter(vcenter_uuid)
    time.sleep(5)

    test_util.test_dsc('check volumes after synchronizing vcenter')
    db_volume = test_lib.lib_get_volume_by_uuid(volume.get_volume().uuid)
    db_volume1 = test_lib.lib_get_volume_by_uuid(volume1.get_volume().uuid)
    if db_volume.status != 'Ready' or db_volume1.status != 'Deleted':
        test_util.test_fail("check data volumes fail after synchronizing vcenter")

    #delete volume file
    volume_installPath = vc_ps.url.split('//')[1] + db_volume.installPath.split('[' + vc_ps.name + ']')[1].lstrip()
    test_util.test_logger(volume_installPath)
    cmd = 'rm -f %s' %volume_installPath
    vchost_user = os.environ['vchostUser']
    vchost_password = os.environ['vchostpwd'] 
    result = test_lib.lib_execute_ssh_cmd(vc_host, vchost_user, vchost_password, cmd, 180)
    

    test_util.test_dsc('Sync vcenter')
    vct_ops.sync_vcenter(vcenter_uuid)
    time.sleep(5)
    db_volume = test_lib.lib_get_volume_by_uuid(volume.get_volume().uuid)
    if db_volume:
        test_util.test_fail("check data volumes fail after synchronizing vcenter")

    #cleanup
    vm.destroy()
    vm.expunge()
    volume1.expunge()

    test_util.test_pass("Test sync volume in vcenter passed.")


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)