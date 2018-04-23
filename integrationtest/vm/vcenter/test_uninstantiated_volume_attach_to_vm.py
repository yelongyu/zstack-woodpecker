'''
test data volume will be instantiated at vm startup in vcenter
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
    network_pattern1 = 'L3-%s'%os.environ['dportgroup']
    if not vct_ops.lib_get_vcenter_l3_by_name(network_pattern1):
        network_pattern1 = 'L3-%s'%os.environ['portgroup0']
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    test_util.test_dsc('Create vm and check')
    vm = test_stub.create_vm_in_vcenter(vm_name = 'test_for_instantiated_vm', image_name = ova_image_name, l3_name = network_pattern1)
    test_obj_dict.add_vm(vm)
    ps_uuid = vm.vm.allVolumes[0].primaryStorageUuid
    vm.check()

    test_util.test_dsc('Create volumes and check')
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_name('vcenter_volume')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()

    volume_creation_option.set_name('vcenter_volume1')
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    volume1 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume1)
    volume1.check()

    test_util.test_dsc('Attach volumes and check')
    volume.attach(vm)
    volume.check()
    vm.stop()
    volume1.attach(vm)
    if volume.volume.installPath == "vcenter://empty" or volume1.volume.installPath != "vcenter://empty":
        test_util.test_fail("check data volumes fail")
    vm.start()
    test_util.test_logger(test_lib.lib_get_volume_by_uuid(volume1.get_volume().uuid))
    db_volume1 = test_lib.lib_get_volume_by_uuid(volume1.get_volume().uuid)
    if db_volume1.installPath == "vcenter://empty":
        test_util.test_fail("check data volumes fail")
    
    #cleanup
    test_lib.lib_error_cleanup(test_obj_dict)

    test_util.test_pass("Test data volume will be instantiated at vm startup in vcenter passed.")


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

