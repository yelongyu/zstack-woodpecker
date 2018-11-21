'''

Test for full clone vm with windows two data volume 

@author: yetian
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict, bs
    #judge whether BS is imagestore
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for i in bs:
        if i.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
	    break
    else:
        test_util.test_logger('BS is type %s.' % i.type)
        test_util.test_skip('Skip test on non-imagestore')

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for i in ps:
        if i.type == 'AliyunNAS':
            test_util.test_skip('Skip test on AliyunNAS PS')
        elif i.type == 'AliyunEBS':
            test_util.test_skip('Skip test on AliyunEBS PS')

    volume_creation_option = test_util.VolumeOption()
    test_util.test_dsc('Create volume and check')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    volume2 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume2.check()
    #volume_uuid = volume.volume.uuid
    #image_name = os.environ.get('imageName_s')
    #l3_name = os.environ.get('l3PublicNetworkName')
    vm = test_stub.create_windows_vm()

    #vm.check()
    test_obj_dict.add_vm(vm)
    volume.attach(vm)
    volume2.attach(vm)
    vm.suspend()

    new_vm = vm.clone(['test_vm_windows_clone_vm1_with_two_data_volume','test_vm_windows_clone_vm2_with_two_data_volume','test_vm_windows_clone_vm3_with_two_data_volume'], full=True)
    for i in new_vm:
    	test_obj_dict.add_vm(i)
    	volumes_number = len(test_lib.lib_get_all_volumes(i.vm))
    	if volumes_number != 3:
        	test_util.test_fail('Did not find 3 volumes for [vm:] %s. But we assigned 3 data volume when create the vm. We only catch %s volumes' % (i.vm.uuid, volumes_number))
    	else:
        	test_util.test_logger('Find 3 volumes for [vm:] %s.' % i.vm.uuid)
    vm.resume()
    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Test clone vm with windows two data volume Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
