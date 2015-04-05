'''

Test Port Forwarding with multi rules connection(including TCP and UDP) with different vips.

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

test_stub = test_lib.lib_get_test_stub()
PfRule = test_state.PfRule
Port = test_state.Port

test_obj_dict = test_state.TestStateDict()

def test():
    '''
        PF test needs at least 3 VR existence. Besides of PF_VM's VR, there 
        are needed another 2 VR VMs. 1st VR public IP address will be set as 
        allowedCidr. The 1st VR VM should be able to access PF_VM. The 2nd VR
        VM should not be able to access PF_VM.
    '''
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

    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    vr2_pub_ip = test_lib.lib_find_vr_pub_ip(vr2)
    
    pf_vm.check()

    vm_nic = pf_vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    pri_l3_uuid = vm_nic.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip1 = test_stub.create_vip('multi_rule_pf1', l3_uuid)
    test_obj_dict.add_vip(vip1)
    vip_uuid1 = vip1.get_vip().uuid

    pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule1_ports, private_target_rule=Port.rule1_ports, vip_uuid=vip_uuid1, vm_nic_uuid=vm_nic_uuid)
    test_pf1 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf1.set_creation_option(pf_creation_opt)
    test_pf1.create(pf_vm)
    vip1.attach_pf(test_pf1)
    vip1.check()

    vip2 = test_stub.create_vip('multi_rule_pf2', l3_uuid)
    test_obj_dict.add_vip(vip2)
    vip_uuid2 = vip2.get_vip().uuid

    pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule2_ports, private_target_rule=Port.rule2_ports, vip_uuid=vip_uuid2, vm_nic_uuid=vm_nic_uuid)
    test_pf2 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf2.set_creation_option(pf_creation_opt)
    test_pf2.create(pf_vm)
    vip2.attach_pf(test_pf2)
    vip2.check()

    vip3 = test_stub.create_vip('multi_rule_pf3', l3_uuid)
    test_obj_dict.add_vip(vip3)
    vip_uuid3 = vip3.get_vip().uuid

    pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.UDP, vip_target_rule=Port.rule2_ports, private_target_rule=Port.rule2_ports, vip_uuid=vip_uuid3, vm_nic_uuid=vm_nic_uuid)
    test_pf3 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf3.set_creation_option(pf_creation_opt)
    test_pf3.create(pf_vm)
    vip3.attach_pf(test_pf3)
    vip3.check()

    vip4 = test_stub.create_vip('multi_rule_pf4', l3_uuid)
    test_obj_dict.add_vip(vip4)
    vip_uuid4 = vip4.get_vip().uuid

    pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.UDP, vip_target_rule=Port.rule3_ports, private_target_rule=Port.rule3_ports, vip_uuid=vip_uuid4, vm_nic_uuid=vm_nic_uuid)
    test_pf4 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf4.set_creation_option(pf_creation_opt)
    test_pf4.create(pf_vm)
    vip4.attach_pf(test_pf4)
    vip4.check()

    pf_vm.check()
    if temp_vm1:
        temp_vm1.destroy()
        test_obj_dict.rm_vm(temp_vm1)
    if temp_vm2:
        temp_vm2.destroy()
        test_obj_dict.rm_vm(temp_vm2)

    test_pf1.delete()
    test_pf2.delete()
    test_pf3.delete()
    test_pf4.delete()
    vip1.delete()
    test_obj_dict.rm_vip(vip1)
    vip2.delete()
    test_obj_dict.rm_vip(vip2)
    vip3.delete()
    test_obj_dict.rm_vip(vip3)
    vip4.delete()
    test_obj_dict.rm_vip(vip4)

    pf_vm.destroy()
    test_obj_dict.rm_vm(pf_vm)

    test_util.test_pass("Test Port Forwarding TCP Rule Successfully")

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
