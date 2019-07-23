'''

New Integration Test for delete VM console password.

@author: Mirabel
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.shell as shell
import zstackwoodpecker.operations.account_operations as acc_ops

test_stub = test_lib.lib_get_specific_stub()

vm1 = None
vm2 = None
password1='111111'

def test():
    from vncdotool import api
    global vm1
    global vm2

    vm1 = test_stub.create_vm()
    vm1.check()
    console = test_lib.lib_get_vm_console_address(vm1.get_vm().uuid)
    test_util.test_logger('[vm:] %s console is on %s:%s' % (vm1.get_vm().uuid, console.hostIp, console.port))
    display = str(int(console.port)-5900)

    test_lib.lib_set_vm_console_password(vm1.get_vm().uuid, password1)
    test_util.test_logger('set [vm:] %s console with password %s' % (vm1.get_vm().uuid, password1))
    vm1.reboot()

    test_lib.lib_delete_vm_console_password(vm1.get_vm().uuid)
    test_util.test_logger('delete [vm:] %s console password after reboot' % (vm1.get_vm().uuid))
    vm1.reboot()
    if not test_lib.lib_wait_target_up(console.hostIp, console.port, timeout=60):
        test_util.test_fail('[vm:] %s console on %s:%s is not connectable' % (vm1.get_vm().uuid, console.hostIp, console.port))

    try:
        client = api.connect(console.hostIp+":"+display)
        client.keyPress('k')
        test_util.test_logger('[vm:] %s console on %s:%s is connectable without password' % (vm1.get_vm().uuid, console.hostIp, console.port))
    except:
        test_util.test_fail('[vm:] %s console on %s:%s is not connectable without password' % (vm1.get_vm().uuid, console.hostIp, console.port))

    vm2 = test_stub.create_vm()
    vm2.check()
    console = test_lib.lib_get_vm_console_address(vm2.get_vm().uuid)
    test_util.test_logger('[vm:] %s console is on %s:%s' % (vm2.get_vm().uuid, console.hostIp, console.port))
    display = str(int(console.port)-5900)

    test_lib.lib_set_vm_console_password(vm2.get_vm().uuid, password1)
    test_util.test_logger('set [vm:] %s console with password %s' % (vm2.get_vm().uuid, password1))
    test_lib.lib_delete_vm_console_password(vm2.get_vm().uuid)
    test_util.test_logger('delete [vm:] %s console password without reboot' % (vm2.get_vm().uuid))
    vm1.reboot()
    if not test_lib.lib_wait_target_up(console.hostIp, console.port, timeout=60):
        test_util.test_fail('[vm:] %s console on %s:%s is not connectable' % (vm2.get_vm().uuid, console.hostIp, console.port))

    try:
        client = api.connect(console.hostIp+":"+display)
        client.keyPress('k')
        test_util.test_logger('[vm:] %s console on %s:%s is connectable without password' % (vm2.get_vm().uuid, console.hostIp, console.port))
    except:
        test_util.test_fail('[vm:] %s console on %s:%s is not connectable without password' % (vm2.get_vm().uuid, console.hostIp, console.port))

    vm1.destroy()
    vm2.destroy()

    test_util.test_pass('Delete VM Console Password Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm1
    global vm2
    if vm1:
        vm1.destroy()
    if vm2:
        vm2.destroy()

