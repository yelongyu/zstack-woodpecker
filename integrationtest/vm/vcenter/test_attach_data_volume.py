'''
test for attaching data volumes to vm
@author: guocan
'''


import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import test_stub
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    global test_obj_dict

    cond = res_ops.gen_query_conditions('name', '=', 'newdatastore')
    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', 'newdatastore (1)')
    ps1_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0].uuid

    centos_image_name = os.environ['image_dhcp_name']
    if os.environ['dportgroup']:
        network_pattern = os.environ['dportgroup']
        network_pattern = 'L3-%s'%network_pattern
    else:
        network_pattern = os.environ['portgroup0']
        network_pattern = 'L3-%s'%network_pattern
    
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    #create vm 
    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm-create', image_name = centos_image_name, l3_name = network_pattern)
    vm.check()
    
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
