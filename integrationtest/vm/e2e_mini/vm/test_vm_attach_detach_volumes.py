# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import vm

vm_ops = None
volume_ops = None
vm_name = 'vm-' + vm.get_time_postfix()
volume_list = ['volume-' + vm.get_time_postfix() for _ in range(2)]

def test():
    global vm_ops
    global volume_ops
    vm_ops = vm.VM()
    volume = test_lib.lib_get_specific_stub(suite_name='e2e_mini/volume', specific_name='volume')
    volume_ops = volume.VOLUME(uri=vm_ops.uri, initialized=True)
    vm_ops.create_vm(vm_name)
    for vol in volume_list:
        volume_ops.create_volume(vol)
    vm_ops.vm_attach_volume(vm_name, volume_list, end_action='close')
    vm_ops.vm_attach_volume(vm_name, volume_list, end_action='cancel')
    vm_ops.vm_attach_volume(vm_name, volume_list)
    vm_ops.vm_attach_volume(vm_name, volume_list, end_action='close')
    vm_ops.vm_attach_volume(vm_name, volume_list, end_action='cancel')
    vm_ops.vm_detach_volume(vm_name, volume_list)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Test VM Attach and Detach Volumes Successful')


def env_recover():
    global vm_ops
    global volume_ops
    vm_ops.expunge_vm(vm_name)
    volume_ops.expunge_volume(volume_list)
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    global volume_ops
    try:
        vm_ops.expunge_vm(vm_name)
        volume_ops.expunge_volume(volume_list)
        vm_ops.close()
    except:
        pass
