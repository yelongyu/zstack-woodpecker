'''

Test create image template from Snapshot. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_vol_header
import zstackwoodpecker.header.volume as vol_header
import zstackwoodpecker.operations.resource_operations as res_ops

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    primary_storage_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for ps in primary_storage_list:
        if ps.type == "AliyunNAS":
            test_util.test_skip('The test is not supported by AliyunNAS primary storage.')

    test_util.test_dsc('Create original vm')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)

    test_util.test_dsc('Construct volume obj.')
    vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
    #root_volume = zstack_vol_header.ZstackTestVolume()
    #root_volume.set_volume(vm_root_volume_inv)
    #root_volume.set_state(vol_header.ATTACHED)
    root_image_uuid = vm_root_volume_inv.rootImageUuid
    vm_img_inv = test_lib.lib_get_image_by_uuid(root_image_uuid)

    test_util.test_dsc('Stop vm before create snapshot.')
    vm.stop()

    test_util.test_dsc('create snapshot and check')
    #snapshots = zstack_sp_header.ZstackVolumeSnapshot()
    #snapshots.set_target_volume(root_volume)
    #test_obj_dict.add_volume_snapshot(snapshots)
    snapshots = test_obj_dict.get_volume_snapshot(vm_root_volume_inv.uuid)
    snapshots.set_utility_vm(vm1)
    snapshots.create_snapshot('create_root_snapshot1')
    snapshots.check()

    snapshot1 = snapshots.get_current_snapshot()
    snapshots.create_snapshot('create_snapshot2')
    snapshots.create_snapshot('create_snapshot3')
    snapshots.check()
    snapshot3 = snapshots.get_current_snapshot()

    test_util.test_dsc('create image template from sp3 and check')
    
    image_option = test_util.ImageOption()
    image_option.set_name('test_snapshot_creating_image')
    image_option.set_guest_os_type(vm_img_inv.guestOsType)
    image_option.set_bits(vm_img_inv.bits)
    image_option.set_root_volume_uuid(snapshot3.get_snapshot().uuid)
    snapshot3.set_image_creation_option(image_option)
    image3 = snapshot3.create_image_template()
    test_obj_dict.add_image(image3)
    image3_uuid = image3.get_image().uuid
    image3.check()

    vm_creation_option = vm.get_creation_option()
    vm_creation_option.set_image_uuid(image3_uuid)
    vm3 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm3)
    vm3.check()

    test_util.test_dsc('create image template from sp1 and check')
    snapshot1.set_image_creation_option(image_option)
    image1 = snapshot3.create_image_template()
    test_obj_dict.add_image(image1)
    image1_uuid = image1.get_image().uuid
    image1.check()

    vm_creation_option.set_image_uuid(image1_uuid)
    vm2 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm2)
    vm2.check()
    
    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    vm2.check()
    vm3.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create image from Snapshot test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
