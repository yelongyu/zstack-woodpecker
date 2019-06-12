'''

Root Volume Image test for Mini

@author: Jiajun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import random

vm = None

def test():
    global vm
    global new_vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name('test_resize_vm')
    vm_creation_option.set_cpu_num(2)
    vm_creation_option.set_memory_size(2147483648)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.stop() 
    vm.check()

    for i in range(1, 20):
        vol_size = test_lib.lib_get_root_volume(vm.get_vm()).size
        volume_uuid = test_lib.lib_get_root_volume(vm.get_vm()).uuid
        if i == 10:
            set_size = vol_size + 21474836480 + random.randint(1,1073741824)
        else:
            set_size = vol_size + random.randint(1,1073741824)

        test_util.test_logger('Resize Root Volume, original size = %s, target size = %s' % (vol_size, set_size))
        vol_ops.resize_volume(volume_uuid, set_size)
        vm.update()
        vol_size_after = test_lib.lib_get_root_volume(vm.get_vm()).size
        if vol_size == vol_size_after:
            test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)

        bs_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
        image_option = test_util.ImageOption()
        image_option.set_root_volume_uuid(volume_uuid)
        image_option.set_name('image_resize_template_small_size_'+vol_size_after)
        image_option.set_backup_storage_uuid_list([bs_list[0].uuid])
        image = img_ops.create_root_volume_template(image_option)

        test_util.test_logger('Resize Root Volume, create VM with template with size = %s' % (set_size))
        vm_creation_option = test_util.VmOption()
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        vm_creation_option.set_l3_uuids([l3_net_uuid])
        vm_creation_option.set_image_uuid(image.uuid)
        vm_creation_option.set_name('test_vm_after_resize_small_size_'+vol_size_after)
        vm_creation_option.set_cpu_num(2)
        vm_creation_option.set_memory_size(2147483648)
        new_vm = test_vm_header.ZstackTestVm()
        new_vm.set_creation_option(vm_creation_option)
        new_vm.create()
        new_vm.check()

        new_volume_uuid = test_lib.lib_get_root_volume_uuid(new_vm.get_vm())
        vol_size_after = test_lib.lib_get_root_volume(new_vm.get_vm()).size
        if vol_size == vol_size_after:
            test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after) 

        new_vm.destroy()
        new_vm.expunge()

    vm.destroy()
    vm.expunge()
    test_util.test_pass('Create Template for Resize VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
