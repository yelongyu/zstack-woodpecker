'''

Test VIP by creating PF and then use the same VIP to create EIP.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import apibinding.inventory as inventory

import os

PfRule = test_state.PfRule
Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    pf_vm = test_stub.create_dnat_vm()
    test_obj_dict.add_vm(pf_vm)

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

    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    vr2_pub_ip = test_lib.lib_find_vr_pub_ip(vr2)
    
    pf_vm.check()

    vm_nic = pf_vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    pri_l3_uuid = vm_nic.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip = test_stub.create_vip('pf_attach_test', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid

    #pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule1_ports, private_target_rule=Port.rule1_ports)
    pf_creation_opt1 = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule4_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip_uuid)
    test_pf1 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf1.set_creation_option(pf_creation_opt1)
    test_pf1.create()
    vip.attach_pf(test_pf1)

    pf_creation_opt2 = PfRule.generate_pf_rule_option(vr2_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule5_ports, private_target_rule=Port.rule5_ports, vip_uuid=vip_uuid)
    test_pf2 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf2.set_creation_option(pf_creation_opt2)
    test_pf2.create()
    vip.attach_pf(test_pf2)

    pf_vm.check()

    test_pf1.attach(vm_nic.uuid, pf_vm)
    test_pf2.attach(vm_nic.uuid, pf_vm)
    vip.check()

    test_pf1.detach()
    test_pf1.delete()
    test_pf2.delete()
    vip.check()

    eip = test_stub.create_eip('create pf/eip test', vip_uuid=vip.get_vip().uuid, vnic_uuid=vm_nic_uuid, vm_obj=pf_vm)
    
    vip.attach_eip(eip)
    vip.check()

    vip.delete()
    test_obj_dict.rm_vip(vip)
    pf_vm.destroy()
    test_obj_dict.rm_vm(pf_vm)

    test_util.test_pass("Test Port Forwarding and EIP with same VIP Successfully")

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
