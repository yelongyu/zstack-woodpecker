'''

New Integration Test for Request access KVM VM console after logout.

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
    acc_ops.logout(session_uuid)
    if test_lib.lib_network_check(console.hostname, console.port):
        test_util.test_fail('[vm:] %s console on %s:%s is connectable, while already logout' % (vm.get_vm().uuid, console.hostname, console.port))
    else:
        test_util.test_log('[vm:] %s console on %s:%s is not connectable' % (vm.get_vm().uuid, console.hostname, console.port))
    vm.destroy()
    vm.check()

    test_util.test_pass('Request Access VM Console after logout Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
