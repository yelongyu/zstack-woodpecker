'''
test for attaching data volumes to vm
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

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    global test_obj_dict

    network_pattern = 'L3-%s'%os.environ['dportgroup']
    if not vct_ops.lib_get_vcenter_l3_by_name(network_pattern):
        network_pattern = 'L3-%s'%os.environ['portgroup0']

    ova_image_name = os.environ['vcenterDefaultmplate']
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    #create vm 
    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm-create', image_name = ova_image_name, l3_name = network_pattern)
    vm.check()
    test_obj_dict.add_vm(vm)
    ps_uuid = vm.vm.allVolumes[0].primaryStorageUuid
    ps1_uuid = None
    for ps in res_ops.query_resource(res_ops.VCENTER_PRIMARY_STORAGE):
        if ps.uuid != ps_uuid:
            ps1_uuid = ps.uuid
            break

    test_util.test_dsc('Create volume and check')
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_name('vcenter_volume')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    volume_creation_option.set_name('vcenter_volume_ps')
    volume_ps = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume_ps)
    volume_ps.check()
    if ps1_uuid:
        volume_creation_option.set_primary_storage_uuid(ps1_uuid)
        volume_creation_option.set_name('vcenter_volume_ps1')
        volume_ps1 = test_stub.create_volume(volume_creation_option)
        test_obj_dict.add_volume(volume_ps1)
        volume_ps1.check()
    
    test_util.test_dsc('Attach volume and check')
    volume.attach(vm)
    volume.check()
    volume_ps.attach(vm)
    volume_ps.check()
    
    if vct_ops.get_datastore_type(os.environ['vcenter']) == 'local' and ps1_uuid != None:
        try:
            volume_ps1.attach(vm)
        except:
            test_util.test_logger('test for volume_ps1 pass')
        else:
            test_util.test_fail('volume_ps1 should not attach to vm')

    
    #cleanup 
    test_lib.lib_error_cleanup(test_obj_dict)
    
    test_util.test_pass("Attach data volumes to vm test passed.")


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)