import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import apibinding.api_actions as api_actions

import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

preallocation_list = ['falloc','metadata','full','none']


def test():
    global vm
    for i in preallocation_list:
        conf_ops.change_global_config("localStoragePrimaryStorage", "qcow2.allocation", i)

        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume = test_stub.create_volume(volume_creation_option)
        test_obj_dict.add_volume(volume)
        volume.check()
        datavolume_uuid = volume.volume.uuid

        vm_create_option = test_util.VmOption()
	image_name = os.environ.get('imageName_net')
    	l3_name = os.environ.get('l3VlanNetworkName1')
    	vm = test_stub.create_vm("test_vm", image_name, l3_name)
    	test_obj_dict.add_vm(vm)
        
	volume.attach(vm)

        volume_uuid = test_lib.lib_get_root_volume(vm.get_vm()).uuid

        snapshots = test_obj_dict.get_volume_snapshot(volume_uuid)
        snapshots.set_utility_vm(vm)
        snapshots.create_snapshot('create_snapshot1')
        snapshots_size = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT)[0].size
	volume_size = test_lib.lib_get_root_volume(vm.get_vm()).size
        if volume_size <= snapshots_size:
                test_util.test_fail('snapshots is not same size as old root volume')

        snapshots = test_obj_dict.get_volume_snapshot(datavolume_uuid)
	snapshots.set_utility_vm(vm)       
        snapshots.create_snapshot('create_snapshot1')
        datasnapshots_size = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT)[1].size
	datavol_size = volume.volume.size
        if datavol_size <= datasnapshots_size:
                test_util.test_fail('snapshots is not same size as old data volume')

        test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('test_pass')
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

