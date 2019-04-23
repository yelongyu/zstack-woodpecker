'''

New Integration Test for resizing root volume.

@author: pengtao.zhang
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

def test():
    global vm
    create_vm_option = test_util.VmOption()
    create_vm_option.set_rootVolume_systemTags(["volumeProvisioningStrategy::ThinProvisioning"])
    create_vm_option.set_name('test_resize_vm_root_volume')
    vm = test_lib.lib_create_vm(create_vm_option)
    vm.check()
    vm.stop() 
    vm.check()

    vol_size = test_lib.lib_get_root_volume(vm.get_vm()).size
    volume_uuid = test_lib.lib_get_root_volume(vm.get_vm()).uuid
    set_size = 1024*1024*1024*5
    vol_ops.resize_volume(volume_uuid, set_size)
    vm.update()
    vol_size_after = test_lib.lib_get_root_volume(vm.get_vm()).size
    if set_size != vol_size_after:
        test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)

    vm.start()
    set_size = 1024*1024*1024*6
    vol_ops.resize_volume(volume_uuid, set_size)
    vm.update()
    vol_size_after = test_lib.lib_get_root_volume(vm.get_vm()).size
    if set_size != vol_size_after:
        test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)

    vm.destroy()
    test_util.test_pass('Resize VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
