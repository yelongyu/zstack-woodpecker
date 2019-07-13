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
    for details_page in [False, True]:
        vm_ops.set_console_password(vm_name, details_page=details_page, end_action='cancel')
        vm_ops.set_console_password(vm_name, details_page=details_page, end_action='close')
        vm_ops.set_console_password(vm_name, details_page=details_page)
        vm_ops.cancel_console_password(vm_name, details_page=details_page, end_action='cancel')
        vm_ops.cancel_console_password(vm_name, details_page=details_page, end_action='close')
        vm_ops.cancel_console_password(vm_name, details_page=details_page)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Set and Cancel the Console  Password of VM Successful')


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
