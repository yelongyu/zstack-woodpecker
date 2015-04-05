'''
Created on Apr. 4 , 2014

Test PF with different VipPortStart/VipPortEnd and 
PrivatePortStart/PrivatePortEnd. For example, the vipPortStart = 1 
vipPortEnd=100, privatePortStart=5001, privatePortEnd=5100

This case might be invalid. It depends on if iptables supports this usage.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
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
    vr1 = test_stub.create_vr_vm(test_obj_dict, l3_name)
    
    l3_name = os.environ.get('l3NoVlanNetworkName1')
    vr2 = test_stub.create_vr_vm(test_obj_dict, l3_name)
    
    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    vr2_pub_ip = test_lib.lib_find_vr_pub_ip(vr2)
    
    pf_vm.check()
    
    vm_nic = pf_vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    pri_l3_uuid = vm_nic.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip = test_stub.create_vip('2 pfs with same vip', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid
    
    #pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule1_ports, private_target_rule=Port.rule1_ports)
    pf_creation_opt1 = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule1_ports, private_target_rule=Port.rule2_ports, vip_uuid=vip_uuid, vm_nic_uuid=vm_nic_uuid)
    test_pf1 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf1.set_creation_option(pf_creation_opt1)
    test_pf1.create(pf_vm)
    vip.attach_pf(test_pf1)
    
    pf_creation_opt2 = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule3_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip_uuid, vm_nic_uuid=vm_nic_uuid)
    test_pf2 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf2.set_creation_option(pf_creation_opt2)
    test_pf2.create(pf_vm)
    vip.attach_pf(test_pf2)
    
    pf_vm.check()
    vip.check()
    
    test_pf1.delete()
    test_pf2.delete()
    import time
    time.sleep(1)
    vip.check()
    pf_vm.destroy()
    test_obj_dict.rm_vm(pf_vm)
    
    vip.delete()
    test_obj_dict.rm_vip(vip)
    test_util.test_pass("Test Port Forwarding TCP Rule Successfully")

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
