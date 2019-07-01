# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import vm

vm_ops = None
vm_name_list = ['vm-' + vm.get_time_postfix() for _ in range(3)]

def test():
    global vm_ops
    vm_ops = vm.VM()
    for vm_name in vm_name_list:
        vm_ops.create_vm(name=vm_name)
    for view in ['card', 'list']:
        vm_ops.delete_vm(vm_name_list, view=view, corner_btn=False)
        vm_ops.resume(vm_name_list, 'vm', view=view)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Batch Delete Resume VMs Test Successful')


def env_recover():
    global vm_ops
    vm_ops.delete_vm(vm_name_list, corner_btn=False)
    vm_ops.expunge_vm(vm_name_list)
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.delete_vm(vm_name_list, corner_btn=False)
        vm_ops.expunge_vm(vm_name_list)
        vm_ops.close()
    except:
        pass
