'''

Test create image template from root volume, after create/delete snapshot 
operations.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_vol_header
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_img_header
import zstackwoodpecker.header.volume as vol_header

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create original vm')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)
    

    test_util.test_dsc('Construct volume obj.')
    vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
    #root_volume = zstack_vol_header.ZstackTestVolume()
    #root_volume.set_volume(vm_root_volume_inv)
    #root_volume.set_target_vm(vm)
    #root_volume.set_state(vol_header.ATTACHED)
    root_volume_uuid = vm_root_volume_inv.uuid
    root_image_uuid = vm_root_volume_inv.rootImageUuid
    vm_img_inv = test_lib.lib_get_image_by_uuid(root_image_uuid)

    test_util.test_dsc('Stop vm before create snapshot.')
    vm.stop()

    test_util.test_dsc('create snapshot')
    #snapshots = zstack_sp_header.ZstackVolumeSnapshot()
    #snapshots.set_target_volume(root_volume)
    #test_obj_dict.add_volume_snapshot(snapshots)
    snapshots = test_obj_dict.get_volume_snapshot(vm_root_volume_inv.uuid)
    snapshots.set_utility_vm(vm1)
    snapshots.create_snapshot('create_root_snapshot1')

    snapshot1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot2')
    snapshot2 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot3')
    snapshot3 = snapshots.get_current_snapshot()

    test_util.test_dsc('delete snapshot3 and create image tempalte from root')
    snapshots.delete_snapshot(snapshot3)

    image_option = test_util.ImageOption()
    image_option.set_name('creating_image_from_root_volume_after_creating_sp')
    image_option.set_guest_os_type(vm_img_inv.guestOsType)
    image_option.set_bits(vm_img_inv.bits)
    image_option.set_root_volume_uuid(root_volume_uuid)
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.get_vm())

    bs_uuid_list = []
    for bs in backup_storage_list:
        bs_uuid_list.append(bs.uuid)
    image_option.set_backup_storage_uuid_list(bs_uuid_list)

    test_util.test_dsc('create image template from root volume')
    image2 = zstack_img_header.ZstackTestImage()
    image2.set_creation_option(image_option)
    image2.create()
    test_obj_dict.add_image(image2)
    image2.check()
    image2_uuid = image2.get_image().uuid
    
    test_util.test_dsc('create vm2 with new created template and check')
    vm_creation_option = vm.get_creation_option()
    vm_creation_option.set_image_uuid(image2_uuid)
    vm2 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm2)
    vm2.check()

    vm2.destroy()
    test_obj_dict.rm_vm(vm2)

    test_util.test_dsc('create snapshot4 and finally delete all snapshots')
    snapshots.create_snapshot('create_snapshot4')
    snapshot4 = snapshots.get_current_snapshot()
    snapshot4.backup()
    snapshots.check()
    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)

    test_util.test_dsc('create image template2 from root volume')
    image3 = zstack_img_header.ZstackTestImage()
    image3.set_creation_option(image_option)
    image3.create()
    test_obj_dict.add_image(image3)
    image3.check()
    image3_uuid = image3.get_image().uuid
    
    test_util.test_dsc('create vm3 with new created template and check')
    vm_creation_option.set_image_uuid(image3_uuid)
    vm3 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm3)
    vm3.check()

    vm3.destroy()
    test_obj_dict.rm_vm(vm3)
    
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create image from root volume with creating/destroying Snapshot Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
