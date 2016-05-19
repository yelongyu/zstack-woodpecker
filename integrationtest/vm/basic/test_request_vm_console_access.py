'''

New Integration Test for Request access KVM VM console.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.shell as shell
import test_stub
import zstackwoodpecker.operations.account_operations as acc_ops

vm = None

def test():
    global vm
    vm = test_stub.create_vm()
    vm.check()
    session_uuid = acc_ops.login_as_admin()
    console = test_lib.lib_request_console_access(vm.get_vm().uuid, session_uuid)
    if test_lib.lib_network_check(console.hostname, console.port):
        test_util.test_logger('[vm:] %s console on %s:%s is connectable' % (vm.get_vm().uuid, console.hostname, console.port))
    else:
        test_util.test_fail('[vm:] %s console on %s:%s is not connectable' % (vm.get_vm().uuid, console.hostname, console.port))
    vm.destroy()
    vm.check()
    if test_lib.lib_network_check(console.hostname, console.port):
        test_util.test_fail('[vm:] %s console on %s:%s is connectable, while VM is already destroyed' % (vm.get_vm().uuid, console.hostname, console.port))
    else:
        test_util.test_logger('[vm:] %s console on %s:%s is not connectable' % (vm.get_vm().uuid, console.hostname, console.port))
    acc_ops.logout(session_uuid)

    test_util.test_pass('Request Access VM Console Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
