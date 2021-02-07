'''

New Integration Test for resizing root volume.

@author: czhou25
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

def test():
    global vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm = test_stub.create_vm("test_resize_vm", image_name, l3_name)
    vm.check()

    vol_size = test_lib.lib_get_root_volume(vm.get_vm()).size
    volume_uuid = test_lib.lib_get_root_volume(vm.get_vm()).uuid
    set_size = 1024*1024*1024*5
    vol_ops.resize_volume(volume_uuid, set_size)
    vm.update()
    vol_size_after = test_lib.lib_get_root_volume(vm.get_vm()).size
    if set_size != vol_size_after:
        test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)

    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    
    vm.update()
    vol_size_after = test_lib.lib_get_root_volume(vm.get_vm()).size
    if set_size != vol_size_after:
        test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)

    vm.destroy()
    test_util.test_pass('Resize VM and Migrate Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
