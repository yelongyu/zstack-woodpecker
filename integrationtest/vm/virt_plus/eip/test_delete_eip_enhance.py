'''

Test create EIP for a VM. 

Test step:
    1. Create a VM
    2. Create a EIP with VM's nic
    3. Check the EIP connectibility
    4. Destroy VM

@author: quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm with EIP and check.')
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    vm_2 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    vm.check()
    vm_2.check()
    test_obj_dict.add_vm(vm)
    test_obj_dict.add_vm(vm_2)
    
    pri_l3_name = os.environ.get('l3VlanNetworkName1')
    pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid

    pub_l3_name = os.environ.get('l3PublicNetworkName')
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid

#add ip range for public network
    ip_range_option = test_util.IpRangeOption()
    ip_range_option.set_l3_uuid(l3_uuid=pub_l3_uuid)
    ip_range_option.set_startIp(startIp='172.24.244.1')
    ip_range_option.set_endIp(endIp='172.24.244.100')
    ip_range_option.set_gateway(gateway='172.24.0.1')
    ip_range_option.set_netmask(netmask='255.255.0.0')
    ip_range_option.set_name(name="test_iprange")
    ip_range = net_ops.add_ip_range(ip_range_option=ip_range_option)
    print "debug ip_range.uuid : %s" % ip_range.uuid

    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    vip = test_stub.create_vip('create_vip_test_1', pub_l3_uuid, required_ip='172.24.244.10')
    test_obj_dict.add_vip(vip)
    eip = test_stub.create_eip('create eip test 1', vip_uuid=vip.get_vip().uuid, vnic_uuid=vm_nic_uuid, vm_obj=vm)
    vip.attach_eip(eip)
    
    vm_nic_2 = vm_2.vm.vmNics[0]
    vm_nic_uuid_2 = vm_nic_2.uuid
    vip_2 = test_stub.create_vip('create_vip_test_2', pub_l3_uuid, required_ip='172.24.244.100')
    test_obj_dict.add_vip(vip_2)
    eip_2 = test_stub.create_eip('create eip test 2', vip_uuid=vip_2.get_vip().uuid, vnic_uuid=vm_nic_uuid_2, vm_obj=vm_2)
    
    vip_2.attach_eip(eip_2)

    if not test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('expected to be able to ping vip while it fail')
    if not test_lib.lib_check_directly_ping(vip_2.get_vip().ip):
        test_util.test_fail('expected to be able to ping vip while it fail')
    eip_2.delete()
    vip_2.delete()
    if not test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('expected to be able to ping vip while it fail')
    vm.destroy()
    test_obj_dict.rm_vm(vm)
    vm_2.destroy()
    test_obj_dict.rm_vm(vm_2)
    if test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('not expected to be able to ping vip while it succeed')

    net_ops.delete_ip_range(ip_range.uuid)
    eip.delete()
    vip.delete()

    test_obj_dict.rm_vip(vip)
    test_obj_dict.rm_vip(vip_2)
    test_util.test_pass('Create EIP for VM Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
