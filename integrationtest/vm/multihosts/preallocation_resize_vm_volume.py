import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.operations.config_operations as conf_ops
import time
import os
import random

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


preallocation_list = ['falloc','metadata','full','none']

def test():
    for i in preallocation_list:
        conf_ops.change_global_config("localStoragePrimaryStorage", "qcow2.allocation", i)

        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume = test_stub.create_volume(volume_creation_option)
        test_obj_dict.add_volume(volume)
        volume.check()
        volume_uuid = volume.volume.uuid
        vol_size = volume.volume.size


        vm_create_option = test_util.VmOption()
        vm = test_lib.lib_create_vm(vm_create_option)
        test_obj_dict.add_vm(vm)
        rootvol_size = test_lib.lib_get_root_volume(vm.get_vm()).size
        rootvolume_uuid = test_lib.lib_get_root_volume(vm.get_vm()).uuid

        volume.attach(vm)

        size = random.randrange(rootvol_size, 40*1024*1024*1024, 4*1024*1024)
        vol_ops.resize_volume(rootvolume_uuid, size)
        vm.update()
        size2 = random.randrange(vol_size, 40*1024*1024*1024, 4*1024*1024)
        vol_ops.resize_data_volume(volume_uuid, size2)
        volume.update()

        volume.detach()

        rootvol_size_after = test_lib.lib_get_root_volume(vm.get_vm()).size
        cond = res_ops.gen_query_conditions('uuid', '=', volume_uuid)
    	data_volume = res_ops.query_resource(res_ops.VOLUME, cond)
    	vol_size_after = data_volume[0].size
        if rootvol_size != rootvol_size_after:
                try:
                        vol_size == vol_size_after
                        test_util.test_fail('Resize Data Volume failed, preallocation value = %s' % i)
                except:
			print("yes")
        else:
        	test_util.test_fail('Resize root Volume failed, size = %s' % rootvol_size_after)
        test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Resize pass' )
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

