'''

New Integration Test for creating KVM VM with console type is spice.

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

    vm_inv=vm.get_vm()
    vm_uuid=vm_inv.uuid
    vm_state = vm.get_vm().state
    host_inv = test_lib.lib_find_host_by_vm(vm_inv)
    host_ip= host_inv.managementIp
    host_username=host_inv.username
    host_password=host_inv.password

    test_util.test_dsc('check the vm console protocol is spice via read xml')
    cmd='''virsh dumpxml %s |grep spice | grep -v spicevmc | grep -v com.redhat.spice.0 |awk  '{print $2}' |awk -F= '{print $2}' '''% (vm_uuid)
    result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd, 180)
    if eval(result) == "spice" :
	print "Vm console protocol is spice, test success"
    else :
	print "Vm console protocol is %s " % eval(result)
	print "test is fail"
        test_util.test_fail('Create VM with spice Test Failed')

    test_util.test_dsc('check the spiceStreamingMode is off via read xml')
    cmd='''virsh dumpxml %s |grep streaming|awk -F/ '{print $1}' |awk -F= '{print $2}' '''% (vm_uuid)
    result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd, 180)
    if eval(result) == "off" :
	print "Vm spiceStreamingMode is off, test success"
    else :
	print "Vm spiceStreamingModeis %s " % eval(result)
	print "test is fail"
        test_util.test_fail('Create VM with spice and spiceStreamingMode is off Test Failed')

    test_util.test_dsc('check the vm console protocol is spice via GetVmConsoleAddressAction')
    if test_stub.get_vm_console_protocol(vm.vm.uuid).protocol == "spice" :
	print "Vm console protocol is spice, test success"
    else :
	print "Vm console protocol is %s " % test_stub.get_vm_console_protocol(vm.vm.uuid).protocol
        print "test is fail"
        test_util.test_fail('Create VM with spice Test Failed')

    vm.destroy()
    vm.check()
    test_util.test_pass('Create VM with spice Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
