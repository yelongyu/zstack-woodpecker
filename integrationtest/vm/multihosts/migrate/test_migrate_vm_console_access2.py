'''

New Integration test for testing console access after vm migration between hosts.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.account_operations as acc_ops

vm = None
test_stub = test_lib.lib_get_specific_stub()

def test():
    global vm
    vm = test_stub.create_vr_vm('migrate_vm', 'imageName_s', 'l3VlanNetwork2')
    vm.check()
    session_uuid = acc_ops.login_as_admin()
    console = test_lib.lib_get_vm_console_address(vm.get_vm().uuid, session_uuid)
    if test_lib.lib_network_check(console.hostIp, console.port):
        test_util.test_logger('[vm:] %s console on %s:%s is connectable' % (vm.get_vm().uuid, console.hostIp, console.port))
    else:
        test_util.test_fail('[vm:] %s console on %s:%s is not connectable' % (vm.get_vm().uuid, console.hostIp, console.port))
    acc_ops.logout(session_uuid)

    test_stub.migrate_vm_to_random_host(vm)

    vm.check()
    session_uuid = acc_ops.login_as_admin()
    console = test_lib.lib_get_vm_console_address(vm.get_vm().uuid, session_uuid)
    if test_lib.lib_network_check(console.hostIp, console.port):
        test_util.test_logger('[vm:] %s console on %s:%s is connectable' % (vm.get_vm().uuid, console.hostIp, console.port))
    else:
        test_util.test_fail('[vm:] %s console on %s:%s is not connectable' % (vm.get_vm().uuid, console.hostIp, console.port))
    acc_ops.logout(session_uuid)

    vm.destroy()
    test_util.test_pass('Migrate VM Console Access Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
