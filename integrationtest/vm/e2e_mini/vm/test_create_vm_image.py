# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import vm

vm_ops = None
vm_name = 'vm-' + vm.get_time_postfix()
vm_image_name = 'vm_image-' + vm.get_time_postfix()

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.create_vm(name=vm_name)
    vm_ops.create_vm_image(vm_name, vm_image_name)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Test Create VM Image Successful')


def env_recover():
    global vm_ops
    global vm_name
    global vm_image_name
    vm_ops.delete_vm(vm_name)
    vm_ops.delete_image(vm_image_name)
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.delete_vm()
        vm_ops.close()
    except:
        pass
