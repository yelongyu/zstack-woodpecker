'''

Test SetVmHostname and get the correct dhcp ip .

@author:
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.host_operations as host_ops

import test_stub

vm = None

def test():
    global vm
    vm = test_stub.create_vm()

    #1
    hostname='vm123.zstack.org'
    vm_ops.set_vm_hostname(vm.get_vm().uuid,'vm123.zstack.org')
    host=test_lib.lib_find_host_by_vm(vm.get_vm())
    host_ops.reconnect_host(host.uuid)

    hostname_inv=vm_ops.get_vm_hostname(vm.get_vm().uuid)
    if hostname_inv != hostname:
        test_util.test_fail('can not get the vm hostname after set vm hostname')

    vm_inv=res_ops.get_resource(res_ops.VM_INSTANCE,uuid=vm.get_vm().uuid)[0]
    if vm_inv.vmNics[0].ip !=vm.get_vm().vmNics[0].ip:
        test_util.test_fail('can not get the correct ip address after set vm hostname and reconnected host')

    #2
    hostname = 'vm1234.zstack.org'
    vm_ops.set_vm_hostname(vm.get_vm().uuid,hostname)
    host=test_lib.lib_find_host_by_vm(vm.get_vm())
    vm_ops.reboot_vm(vm.get_vm().uuid)

    hostname_inv=vm_ops.get_vm_hostname(vm.get_vm().uuid)
    if hostname_inv != hostname:
        test_util.test_fail('can not get the vm hostname after set vm hostname')

    vm_inv=res_ops.get_resource(res_ops.VM_INSTANCE,uuid=vm.get_vm().uuid)[0]
    if vm_inv.vmNics[0].ip !=vm.get_vm().vmNics[0].ip:
        test_util.test_fail('can not get the correct ip address after set vm hostname and reboot vm')

    #3
    hostname = 'vm12345.zstack.org'
    vm_ops.set_vm_hostname(vm.get_vm().uuid, hostname)
    host = test_lib.lib_find_host_by_vm(vm.get_vm())
    host_ops.reconnect_host(host.uuid)
    vm_ops.reboot_vm(vm.get_vm().uuid)

    hostname_inv = vm_ops.get_vm_hostname(vm.get_vm().uuid)
    if hostname_inv != hostname:
        test_util.test_fail('can not get the vm hostname after set vm hostname')

    vm_inv = res_ops.get_resource(res_ops.VM_INSTANCE, uuid=vm.get_vm().uuid)[0]
    if vm_inv.vmNics[0].ip != vm.get_vm().vmNics[0].ip:
        test_util.test_fail('can not get the correct ip address after set vm hostname and reboot vm and reconnect host')

    test_util.test_pass('SetVMHostname and get vm\'s correct ip')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
