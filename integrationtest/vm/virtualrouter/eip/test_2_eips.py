'''

Test create 2 EIPs for 2 Vms in same L3 Network. So 2 VIPs will be setup in same VR
, then check if 2 VM could use VIP to connect each other. 

Test step:
    1. Create 2 VMs
    2. Create a EIP with VM's nic each
    3. Check the 2 EIPs connectibility
    4. Destroy VMs

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm with EIP and check.')
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm2)
    
    l3_name = os.environ.get('l3VlanNetworkName1')
    vr1_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr1_l3_uuid)
    temp_vm1 = None
    if not vrs:
        #create temp_vm1 for getting vlan1's vr for test pf_vm portforwarding
        temp_vm1 = test_stub.create_vlan_vm()
        test_obj_dict.add_vm(temp_vm1)
        vr1 = test_lib.lib_find_vr_by_vm(temp_vm1.vm)[0]
    else:
        vr1 = vrs[0]

    l3_name = os.environ.get('l3NoVlanNetworkName1')
    vr2_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr2_l3_uuid)
    temp_vm2 = None
    if not vrs:
        #create temp_vm2 for getting novlan's vr for test pf_vm portforwarding
        temp_vm2 = test_stub.create_user_vlan_vm()
        test_obj_dict.add_vm(temp_vm2)
        vr2 = test_lib.lib_find_vr_by_vm(temp_vm2.vm)[0]
    else:
        vr2 = vrs[0]

    #we do not need temp_vm1 and temp_vm2, since we just use their VRs.
    if temp_vm1:
        temp_vm1.destroy()
        test_obj_dict.rm_vm(temp_vm1)
    if temp_vm2:
        temp_vm2.destroy()
        test_obj_dict.rm_vm(temp_vm2)

    vm_nic1 = vm1.vm.vmNics[0]
    vm_nic1_uuid = vm_nic1.uuid
    vm_nic2 = vm2.vm.vmNics[0]
    vm_nic2_uuid = vm_nic2.uuid
    pri_l3_uuid = vm_nic1.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip1 = test_stub.create_vip('create_vip 1', l3_uuid)
    test_obj_dict.add_vip(vip1)
    eip1 = test_stub.create_eip('create eip 1', vip_uuid=vip1.get_vip().uuid, \
            vnic_uuid=vm_nic1_uuid, vm_obj=vm1)
    vip1.attach_eip(eip1)
    
    vip2 = test_stub.create_vip('create_vip 2', l3_uuid)
    test_obj_dict.add_vip(vip2)
    eip2 = test_stub.create_eip('create eip 2', vip_uuid=vip2.get_vip().uuid, \
            vnic_uuid=vm_nic2_uuid, vm_obj=vm2)
    vip2.attach_eip(eip2)
    
    vm1.check()
    vip1.check()
    vm2.check()
    vip2.check()

    test_lib.lib_check_ports_in_a_command(vm1.get_vm(), vip1.get_vip().ip, \
            vip2.get_vip().ip, test_stub.target_ports, [], vm2.get_vm())

    test_lib.lib_check_ports_in_a_command(vm2.get_vm(), vip2.get_vip().ip, \
            vip1.get_vip().ip, test_stub.target_ports, [], vm1.get_vm())

    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    test_lib.lib_check_ports_in_a_command(vm2.get_vm(), vip2.get_vip().ip, \
            vip1.get_vip().ip, [], test_stub.target_ports, vm1.get_vm())

    vm2.destroy()
    test_obj_dict.rm_vm(vm2)

    vip1.delete()
    test_obj_dict.rm_vip(vip1)
    vip2.delete()
    test_obj_dict.rm_vip(vip2)
    test_util.test_pass('Test 2 EIPs for 2 VMs Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
