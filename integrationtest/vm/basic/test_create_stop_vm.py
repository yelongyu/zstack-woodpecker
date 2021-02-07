'''

New Integration Test for creating KVM stop VM.

@author: yetian
'''

import zstackwoodpecker.test_util as test_util
import test_stub

vm = None

def test():
    global vm
    vm = test_stub.create_stop_vm()
    if vm.vm.state == "Stopped":
       print "vm state is Stopped"
    else:
       test_util.test_fail("vm state is not Stopped")
    vm.start()
    if vm.vm.state == "Running":
       print "start vm state is Running"
    else:
       test_util.test_fail("vm state is not Running")
    vm.stop()
    vm.destroy()
    vm.check()
    test_util.test_pass('Create stop VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
