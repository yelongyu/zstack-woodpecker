'''

New Integration Test for Request access multiple KVM VM console.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.shell as shell
import test_stub

vms = []

def test():
    global vms
    for i in range(12):
        vms.append(test_stub.create_vm())

    for vm in vms:
        if vm:
            vm.check()
            console = test_lib.lib_request_console_access(vm.get_vm().uuid)
            if test_lib.lib_network_check(console.hostname, console.port):
                test_util.test_logger('[vm:] %s console on %s:%s is connectable' % (vm.get_vm().uuid, console.hostname, console.port))
            else:
                test_util.test_fail('[vm:] %s console on %s:%s is not connectable' % (vm.get_vm().uuid, console.hostname, console.port))

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
