'''

New Integration Test for creating KVM VM.

@author: ye.tian
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib

vm = None

def test():
    global vm
    vm = test_stub.create_spice_vm()
    vm.check()
    test_stub.check_vm_spice(vm.vm.uuid)

    vm_inv=vm.get_vm()
    vm_uuid=vm_inv.uuid
    vm_state = vm.get_vm().state

    host_inv = test_lib.lib_find_host_by_vm(vm_inv)
    host_ip= host_inv.managementIp
    host_username=host_inv.username
    host_password=host_inv.password

    test_util.test_dsc('check the vm console protocol is spice')
    cmd='virsh dumpxml %s |grep spice'% (vm_uuid)
    result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd, 180)
    print cmd
    print result

    vm.destroy()
    vm.check()
    test_util.test_pass('Create VM with spice Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
