'''

Create Volume Template from Root Volume

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.header.volume as volume_header
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm and check')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)

    vm.stop()
    r_volume = zstack_volume_header.ZstackTestVolume()
    r_volume.set_volume(test_lib.lib_get_root_volume(vm.get_vm()))
    r_volume.set_state(volume_header.ATTACHED)

    test_util.test_dsc('Create volume template and check')
    bs_list = test_lib.lib_get_backup_storage_list_by_vm(vm.get_vm())
    vol_tmpt = r_volume.create_template([bs_list[0].uuid], 'new_data_template')
    test_obj_dict.add_image(vol_tmpt)
    vol_tmpt.check()

    test_util.test_dsc('Create volume from template and check')
    ps_uuid = vm.get_vm().allVolumes[0].primaryStorageUuid
    volume = vol_tmpt.create_data_volume(ps_uuid, 'new_volume_from_template1')
    test_obj_dict.add_volume(volume)

    volume2 = vol_tmpt.create_data_volume(ps_uuid, 'new_volume_from_template2')
    test_obj_dict.add_volume(volume2)
    volume2.check()
    volume.attach(vm)
    vm.start()
    volume2.attach(vm)
    vm.check()
    volume.check()
    volume2.check()
    volume.detach()
    volume.delete()
    test_obj_dict.rm_volume(volume)
    volume2.detach()
    volume2.delete()
    test_obj_dict.rm_volume(volume2)

    vol_tmpt.delete()
    test_obj_dict.rm_image(vol_tmpt)
    vm.destroy()
    test_util.test_pass('Create Data Volume Template from Data Volume Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
