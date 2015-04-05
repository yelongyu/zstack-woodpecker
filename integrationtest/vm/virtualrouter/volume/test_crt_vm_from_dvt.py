'''

Create VM from Data Volume Template. This should be fail. It comes from a bug.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
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

    test_util.test_dsc('Try to use data vol_tempt to Create VM. ')
    vm_option = vm.get_creation_option()
    vm_option.set_image_uuid(vol_tmpt.get_image().uuid)
    vm2 = zstack_vm_header.ZstackTestVm()
    vm2.set_creation_option(vm_option)
    try:
        vm2.create()
    except:
        test_util.test_logger('Expected exception, when creating VM by using Data Volume Template as root image')
    else:
        test_util.test_fail('VM can use data volume template to create VM')

    vol_tmpt.delete()
    test_obj_dict.rm_image(vol_tmpt)
    vm.destroy()
    test_util.test_pass('Create VM from Data Volume Template Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
