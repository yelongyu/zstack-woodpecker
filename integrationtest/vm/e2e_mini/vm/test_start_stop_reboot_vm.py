# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import vm

vm_ops = None
vm_name = 'vm-' + vm.get_time_postfix()

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.create_vm(name=vm_name)
    vm_ops.vm_ops(vm_name, action='stop')
    vm_ops.vm_ops(vm_name, action='start')
    vm_ops.vm_ops(vm_name, action='reboot')
    vm_ops.vm_ops(vm_name, action='stop', details_page=True)
    vm_ops.vm_ops(vm_name, action='start', details_page=True)
    vm_ops.vm_ops(vm_name, action='reboot', details_page=True)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Start, Stop and Reboot VM Successful')


def env_recover():
    global vm_ops
    vm_ops.expunge_vm(vm_name)
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.expunge_vm(vm_name)
        vm_ops.close()
    except:
        pass
