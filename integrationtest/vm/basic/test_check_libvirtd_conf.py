'''

New Integration Test for creating KVM VM.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import test_stub

vm = None

def test():
    global vm
    vm = test_stub.create_vm()
    vm.check()
    cmd = 'grep "^host_uuid" /etc/libvirt/libvirtd.conf'
    host = test_lib.lib_find_host_by_vm(vm.get_vm())
    if not test_lib.lib_execute_ssh_cmd(host, "root", "password", cmd):
    	test_util.test_fail("Check host_uuid in libvirtd.conf failed")
    test_util.test_pass('Check host_uuid in libvirtd Success')
    vm.destroy()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
