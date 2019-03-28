'''
Test create image template from root volume, after create/delete snapshot 
operations.

This bug is coming from a robot test failure:

Robot Action: create_vm  
Robot Action Result: create_vm; new VM: fc2c0221be72423ea303a522fd6570e9 
Robot Action: stop_vm; on VM: fc2c0221be72423ea303a522fd6570e9 
Robot Action: create_volume_snapshot; on Root Volume: fe839dcb305f471a852a1f5e21d4feda; on VM: fc2c0221be72423ea303a522fd6570e9 
Robot Action Result: create_volume_snapshot; new SP: 497ac6abaf984f5a825ae4fb2c585a88 
Robot Action: create_data_volume_template_from_volume; on Volume: fe839dcb305f471a852a1f5e21d4feda;  on VM: fc2c0221be72423ea303a522fd6570e9 
Robot Action Result: create_data_volume_template_from_volume; new DataVolume Image: fb23cdfce4b54072847a3cfe8ae45d35 
Robot Action: destroy_vm; on VM: fc2c0221be72423ea303a522fd6570e9 
Robot Action: create_data_volume_from_image; on Image: fb23cdfce4b54072847a3cfe8ae45d35 
Robot Action Result: create_data_volume_from_image; new Volume: 20dee895d68b428a88e5ec3d3ef634d8 
Robot Action: create_volume_snapshot; on Volume: 20dee895d68b428a88e5ec3d3ef634d8 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_vol_header
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_img_header
import zstackwoodpecker.header.header as zstack_header
import zstackwoodpecker.header.volume as vol_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import apibinding.inventory as inventory

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create original vm')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm.stop()
    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)
    
    vm1.check()
    test_util.test_dsc('create snapshot for root volume')
    vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
    snapshots_root = test_obj_dict.get_volume_snapshot(vm_root_volume_inv.uuid)
    snapshots_root.set_utility_vm(vm1)
    test_obj_dict.add_volume_snapshot(snapshots_root)
    snapshots_root.create_snapshot('create_root_snapshot1')

    test_util.test_dsc('create image template from root volume')
    root_volume_uuid = vm_root_volume_inv.uuid
    root_image_uuid = vm_root_volume_inv.rootImageUuid
    vm_img_inv = test_lib.lib_get_image_by_uuid(root_image_uuid)
    image_option = test_util.ImageOption()
    image_option.set_name('creating_image_from_root_volume')
    image_option.set_guest_os_type(vm_img_inv.guestOsType)
    image_option.set_bits(vm_img_inv.bits)
    image_option.set_root_volume_uuid(root_volume_uuid)
    image_option.set_timeout('600000')
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.get_vm())
    bs_uuid_list = []
    for bs in backup_storage_list:
        bs_uuid_list.append(bs.uuid)
    image_option.set_backup_storage_uuid_list(bs_uuid_list)
    image = zstack_img_header.ZstackTestImage()
    image.set_creation_option(image_option)
    image.create()
    if test_lib.lib_get_delete_policy('image') != zstack_header.DELETE_DIRECT:
        test_obj_dict.add_image(image)
    image.delete()

    test_util.test_dsc('Construct volume obj.')
    r_volume = zstack_volume_header.ZstackTestVolume()
    r_volume.set_volume(test_lib.lib_get_root_volume(vm.get_vm()))
    r_volume.set_state(vol_header.ATTACHED)

    test_util.test_dsc('Create volume template')
    bs_list = test_lib.lib_get_backup_storage_list_by_vm(vm.get_vm())
    vol_tmpt = r_volume.create_template([bs_list[0].uuid], 'new_data_template_by_root_volume')
    if test_lib.lib_get_delete_policy('image') != zstack_header.DELETE_DIRECT:
        test_obj_dict.add_image(vol_tmpt)

    #destroy vm
    host_uuid = test_lib.lib_get_vm_host(vm.get_vm()).uuid
    vm.destroy()

    test_util.test_dsc('Create volume from template')
    ps_uuid = vm.get_vm().allVolumes[0].primaryStorageUuid
    ps = test_lib.lib_get_primary_storage_by_uuid(ps_uuid)

    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        volume = vol_tmpt.create_data_volume(ps_uuid, 'new_data_volume_from_template1', host_uuid)
    else:
        volume = vol_tmpt.create_data_volume(ps_uuid, 'new_data_volume_from_template1')

    test_obj_dict.add_volume(volume)
    vol_tmpt.delete()

    test_util.test_dsc('create snapshot')
    snapshots = zstack_sp_header.ZstackVolumeSnapshot()
    snapshots.set_target_volume(volume)
    snapshots.set_utility_vm(vm1)
    test_obj_dict.add_volume_snapshot(snapshots)
    snapshots.create_snapshot('create_snapshot1')

    snapshot1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot2')
    snapshot2 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot3')
    snapshot3 = snapshots.get_current_snapshot()

    test_util.test_dsc('delete snapshot3')
    snapshots.delete_snapshot(snapshot3)

    snapshots.check()
    test_obj_dict.rm_volume_snapshot(snapshots)

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create snapshot from a volume, which is created from data volume template, which is create from a root volume Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
