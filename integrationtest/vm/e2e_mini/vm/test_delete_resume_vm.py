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

    for view in ['card', 'list']:
        # Delete button
        vm_ops.delete_vm(vm_name, view=view)
        # Resume button
        vm_ops.resume(vm_name, 'vm', view=view)

        # Delete via more operation
        vm_ops.delete_vm(vm_name, view=view, corner_btn=False)
        # Resume by more ops
        vm_ops.resume(vm_name, 'vm', view=view, details_page=True)

        # Delete via more operation in details page
        vm_ops.delete_vm(vm_name, view=view, corner_btn=False, details_page=True)
        # Resume button
        vm_ops.resume(vm_name, 'vm', view=view)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Delete Resume VM Test Successful')


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