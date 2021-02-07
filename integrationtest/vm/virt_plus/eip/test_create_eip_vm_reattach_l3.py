'''

Test detach l3 and attach l3 that same EIP attach again for a VM.

Test step:
    1. Create a VM
    2. Create a EIP with VM's nic
    3. Check the EIP connectibility
    4. Detach L3 of VM
    5. Check the EIP connectibility which expect fail
    6. Attach L3 of VM
    7. Attach same EIP of VM
    8. Check the EIP connectibility which expect fail
    9. Destroy VM

@author: quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import os
import tempfile

test_stub = test_lib.lib_get_specific_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm with EIP and check.')
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm)

    pri_l3_name = os.environ.get('l3VlanNetworkName1')
    pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid

    pub_l3_name = os.environ.get('l3PublicNetworkName')
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid

    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    vip = test_stub.create_vip('create_eip_test', pub_l3_uuid)
    test_obj_dict.add_vip(vip)
    eip = test_stub.create_eip('create eip test', vip_uuid=vip.get_vip().uuid, vnic_uuid=vm_nic_uuid, vm_obj=vm)

    vip.attach_eip(eip)

    vm.check()
    if not test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('expected to be able to ping vip while it fail')

    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('ping -c 4 223.5.5.5')
    script_file.close()
    if not test_lib.lib_execute_shell_script_in_vm(vm.get_vm(), script_file.name):
        test_util.test_fail("fail to tracepath in [vm:] %s" % (vm.get_vm().uuid))
    os.unlink(script_file.name)

    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('''
while [ 1 -eq 1 ]; do
	route -n | grep 0.0.0.0
	if [ $? -ne 0 ]; then
		pkill dhclient
		dhclient
	fi
	sleep 40
done
''')
    script_file.close()
    try:
        test_lib.lib_execute_shell_script_in_vm(vm.get_vm(), script_file.name, timeout=2)
    except:
        test_util.test_logger('ignore')
    os.unlink(script_file.name)

    net_ops.detach_l3(vm_nic_uuid)
    if test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('expected to not be able to ping vip while it success')

    #vm.stop()
    net_ops.attach_l3(pri_l3_uuid, vm.get_vm().uuid)

    #vm.start()
    vm.check()
    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    net_ops.attach_eip(eip.get_eip().uuid, vm_nic_uuid)
    vm.check()
    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('ping -c 4 223.5.5.5')
    script_file.close()
    if not test_lib.lib_execute_shell_script_in_vm(vm.get_vm(), script_file.name):
        test_util.test_fail("fail to tracepath in [vm:] %s" % (vm.get_vm().uuid))
    os.unlink(script_file.name)

    if not test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('expected to be able to ping vip while it fail')

    vm.destroy()
    test_obj_dict.rm_vm(vm)
    if test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('not expected to be able to ping vip while it succeed')

    eip.delete()
    vip.delete()

    test_obj_dict.rm_vip(vip)
    test_util.test_pass('Create EIP for VM Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

