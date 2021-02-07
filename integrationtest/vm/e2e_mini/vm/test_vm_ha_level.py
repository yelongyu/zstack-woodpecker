# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

vm = test_lib.lib_get_specific_stub('e2e_mini/vm', 'vm')

vm_ops = None
vm_name = 'vm-' + vm.get_time_postfix()

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.create_vm(name=vm_name)
    vm_ops.set_ha_level(vm_name=vm_name, ha=True)
    vm_ops.set_ha_level(vm_name=vm_name, ha=False)
    vm_ops.set_ha_level(vm_name=vm_name, ha=True, details_page=True)
    vm_ops.set_ha_level(vm_name=vm_name, ha=False, details_page=True)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Set VM HA Level Successful')


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
