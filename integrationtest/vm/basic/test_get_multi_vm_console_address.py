'''

New Integration Test for Request access multiple KVM VM console.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.shell as shell
import zstackwoodpecker.operations.account_operations as acc_ops

test_stub = test_lib.lib_get_specific_stub()

vms = []

def test():
    global vms
    for i in range(6):
        vms.append(test_stub.create_vm())

    session_uuid = acc_ops.login_as_admin()
    for vm in vms:
        if vm:
            vm.check()
            console = test_lib.lib_get_vm_console_address(vm.get_vm().uuid, session_uuid)
            if test_lib.lib_network_check(console.hostIp, console.port):
                test_util.test_logger('[vm:] %s console on %s:%s is connectable' % (vm.get_vm().uuid, console.hostIp, console.port))
            else:
                test_util.test_fail('[vm:] %s console on %s:%s is not connectable' % (vm.get_vm().uuid, console.hostIp, console.port))
    acc_ops.logout(session_uuid)

    for vm in vms:
        if vm:
            vm.destroy()
            vm.check()
    test_util.test_pass('Request Access Multiple VM Console Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vms

    for vm in vms:
        if vm:
            vm.destroy()

