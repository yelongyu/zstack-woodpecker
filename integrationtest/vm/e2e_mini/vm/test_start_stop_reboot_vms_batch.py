# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

vm = test_lib.lib_get_specific_stub('e2e_mini/vm', 'vm')

vm_ops = None
vm_name_list = ['vm-' + vm.get_time_postfix() for _ in range(3)]

def test():
    global vm_ops
    vm_ops = vm.VM()
    for vm_name in vm_name_list:
        vm_ops.create_vm(name=vm_name)
    vm_ops.vm_ops(vm_name_list, action='stop')
    vm_ops.vm_ops(vm_name_list, action='start')
    vm_ops.vm_ops(vm_name_list, action='reboot')
    vm_ops.check_browser_console_log()
    test_util.test_pass('Start, Stop and Reboot VMs in Batches Successful')


def env_recover():
    global vm_ops
    vm_ops.expunge_vm(vm_name_list)
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.expunge_vm(vm_name_list)
        vm_ops.close()
    except:
        pass
