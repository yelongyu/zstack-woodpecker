'''

Test for full clone vm with one data volume on local

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
    global test_obj_dict
    #judge whether BS is imagestore
    bs = res_ops.query_resource(res_ops.IMAGE_STORE_BACKUP_STORAGE)[0]
    if bs.type != inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
        test_util.test_skip('Skip test on non-imagestore')

    volume_creation_option = test_util.VolumeOption()
    test_util.test_dsc('Create volume and check')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume_uuid = volume.volume.uuid
    vol_size = volume.volume.size
    image_name = os.environ.get('imageName_s')
    l3_name = os.environ.get('l3PublicNetworkName')
    vm = test_stub.create_vm("test_vm", image_name, l3_name)
    #vm.check()
    test_obj_dict.add_vm(vm)
    volume.attach(vm)

    new_vm = vm.clone(['test_vm_clone_vm1_with_one_data_volume','test_vm_clone_vm2_with_one_data_volume','test_vm_clone_vm3_with_one_data_volume'], full=True)
    for i in new_vm:
    	test_obj_dict.add_vm(i)
    	volumes_number = len(test_lib.lib_get_all_volumes(i.vm))
    	if volumes_number != 2:
        	test_util.test_fail('Did not find 2 volumes for [vm:] %s. But we assigned 2 data volume when create the vm. We only catch %s volumes' % (i.vm.uuid, volumes_number))
    	else:
        	test_util.test_logger('Find 2 volumes for [vm:] %s.' % i.vm.uuid)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Test full clone 3vms with one data volume Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
