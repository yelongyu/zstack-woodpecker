'''

Test for full clone stop vm with one data volume on local

@author: yetian
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
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
    vm.suspend()
    new_vm = vm.clone(['test_vm_clone_with_one_data_volume'], full=True)[0]
    test_obj_dict.add_vm(new_vm)

    volumes_number = len(test_lib.lib_get_all_volumes(new_vm.vm))
    if volumes_number != 2:
        test_util.test_fail('Did not find 2 volumes for [vm:] %s. But we assigned 2 data volume when create the vm. We only catch %s volumes' % (new_vm.vm.uuid, volumes_number))
    else:
        test_util.test_logger('Find 2 volumes for [vm:] %s.' % new_vm.vm.uuid)

    #Set_size = 1024*1024*1024*5
    #Vol_ops.resize_data_volume(volume_uuid, set_size)
    #Vm.update()
    #Vol_size_after = test_lib.lib_get_data_volumes(vm.get_vm())[0].size
    #If set_size != vol_size_after:
    #    test_util.test_fail('Resize Data Volume failed, size = %s' % vol_size_after)

    #Volume.detach()
    #Vm.update()
    #Target_host = test_lib.lib_find_random_host(vm.get_vm())
    #Vol_ops.migrate_volume(volume_uuid, target_host.uuid)

    #Cond = res_ops.gen_query_conditions('uuid', '=', volume_uuid)
    #Data_volume = res_ops.query_resource(res_ops.VOLUME, cond)
    #Vol_size_after = data_volume[0].size
    #If set_size != vol_size_after:
    #    test_util.test_fail('Resize Data Volume failed, size = %s' % vol_size_after)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Test clone vm with one data volume Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
