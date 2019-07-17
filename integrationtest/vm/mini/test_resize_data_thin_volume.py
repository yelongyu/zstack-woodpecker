'''

New Integration Test for resizing data volume.

@author: czhou25
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    test_util.test_dsc('Create volume and check')
    volume = test_stub.create_volume(provisioning="thin")
    test_obj_dict.add_volume(volume)
    volume.check()
    volume_uuid = volume.volume.uuid
    vol_size = volume.volume.size
    image_name = os.environ.get('imageName_net')
    l3_name = os.environ.get('l3VlanNetworkName1')
    create_vm_option = test_util.VmOption()
    create_vm_option.set_name('test_resize_vm_root_volume')
    vm = test_lib.lib_create_vm(create_vm_option)
#    vm = test_stub.create_vm("test_resize_vm", image_name, l3_name)
    vm.check()
    test_obj_dict.add_vm(vm)
    volume.attach(vm)
    vm.stop()
    vm.check()

    set_size = 1024*1024*1024*5
    vol_ops.resize_data_volume(volume_uuid, set_size)
    vm.update()
    vol_size_after = test_lib.lib_get_data_volumes(vm.get_vm())[0].size
    if set_size != vol_size_after:
        test_util.test_fail('Resize Data Volume failed, size = %s' % vol_size_after)

    vm.start()
    vm.check()
    set_size = 1024*1024*1024*6
    vol_ops.resize_data_volume(volume_uuid, set_size)
    vm.update()
    vol_size_after = test_lib.lib_get_data_volumes(vm.get_vm())[0].size
    if set_size != vol_size_after:
        test_util.test_fail('Resize Data Volume failed, size = %s' % vol_size_after)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Resize Data Volume Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
