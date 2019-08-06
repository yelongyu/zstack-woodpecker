import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.account_operations as acc_ops
import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as conf_ops
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

preallocation_list = ['full','falloc','metadata','none']

def test():
    for i in preallocation_list:
        conf_ops.change_global_config("localStoragePrimaryStorage", "qcow2.allocation", i)

        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume = test_stub.create_volume(volume_creation_option)
        test_obj_dict.add_volume(volume)
        volume.check()
        datavolume_uuid = volume.volume.uuid
        
        
        vm_create_option = test_util.VmOption()
        vm = test_lib.lib_create_vm(vm_create_option)
        test_obj_dict.add_vm(vm)
        root_volume_uuid = test_lib.lib_get_root_volume(vm.vm).uuid

	volume.attach(vm)	
		
	bs_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
        image_option = test_util.ImageOption()
	image_option.set_backup_storage_uuid_list([bs_list[0].uuid])

        new_image = test_lib.lib_create_template_from_volume(root_volume_uuid)
        image_size = res_ops.query_resource(res_ops.IMAGE)[0].size


	image_option.set_data_volume_uuid(datavolume_uuid)
	image_option.set_name('data_template')
	data_image = img_ops.create_data_volume_template(image_option)
        dataimage_size = res_ops.query_resource(res_ops.IMAGE)[1].size

        rootvolume_disksize = test_lib.lib_get_root_volume(vm.get_vm()).size
        cond = res_ops.gen_query_conditions('uuid', '=', datavolume_uuid)
        data_volume = res_ops.query_resource(res_ops.VOLUME, cond)
        vol_actualSize = data_volume[0].size
        if rootvolume_disksize <= image_size and vol_actualSize <= dataimage_size:
            test_util.test_pass('template Succeed')


        est_lib.lib_error_cleanup(test_obj_dict)

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
