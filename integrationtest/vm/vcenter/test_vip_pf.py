'''

Test Attach/Detach Port Forwarding with VR's pub IP

@author: moyu
'''


import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import apibinding.inventory as inventory

import time
import os
import threading


test_lib.TestHarness = test_lib.TestHarnessVR

PfRule = test_state.PfRule
Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vm1 = None
vm2 = None
vip = None

def test():
    global vm1, vm2, vip

    l3_vr_network = os.environ['l3vCenterNoVlanNetworkName']
    image_name = os.environ['image_dhcp_name']

    # create vm1 vm2
    vm1 = test_stub.create_vm_in_vcenter(vm_name='test_vm1', image_name = image_name, l3_name=l3_vr_network)
    vm2 = test_stub.create_vm_in_vcenter(vm_name='test_vm2', image_name = image_name, l3_name=l3_vr_network)
    test_obj_dict.add_vm(vm1)
    test_obj_dict.add_vm(vm2)
    vm1.check()
    vm2.check()

    l3_vr_network = os.environ['l3vCenterNoVlanNetworkName1']
    vr1 = test_stub.create_vm_in_vcenter(vm_name='vm1', image_name = image_name, l3_name=l3_vr_network)
    l3_vr_network = os.environ['l3vCenterNoVlanNetworkName2']
    vr2 = test_stub.create_vm_in_vcenter(vm_name='vm2', image_name = image_name, l3_name=l3_vr_network)
    test_obj_dict.add_vm(vr1)
    test_obj_dict.add_vm(vr2)
    
   
    vr1_nic = vr1.get_vm().vmNics[0] 
    pri_l3_uuid = vr1_nic.l3NetworkUuid
    vr1 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)

    vr2_nic = vr2.get_vm().vmNics[0]
    pri_l3_uuid = vr2_nic.l3NetworkUuid
    vr2 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr2_pub_ip = test_lib.lib_find_vr_pub_ip(vr2)

    vm1_nic = vm1.get_vm().vmNics[0]
    vm1_nic_uuid = vm1_nic.uuid
    vm2_nic = vm2.get_vm().vmNics[0]
    vm2_nic_uuid = vm2_nic.uuid

    pri_l3_uuid = vm1_nic.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_ip = test_lib.lib_find_vr_pub_ip(vr)

    vip = zstack_vip_header.ZstackTestVip()
    vip.get_snat_ip_as_vip(vr_pub_ip)
    vip.isVcenter = True
    vip_uuid = vip.get_vip().uuid

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

    vm1.check()
    vip.check()

    # pf_1_attach_vm1 pf_2_attach_vm2
    test_pf1.attach(vm1_nic_uuid, vm1)
    test_pf2.attach(vm2_nic_uuid, vm2)
    vip.check()

    vm1.stop()
    vip.check()

    # pf_1_detach pf_1_attach_vm2
    test_pf1.detach()
    vip.check()
    test_pf1.attach(vm2_nic_uuid, vm2)
    vip.check()

    vm1.start()
    time.sleep(30)
    vip.check()
    vm1.stop()

    test_pf1.detach()
    test_pf2.detach()
    vip.check()

    # pf_1_attach_vm1 pf_2_attach_vm1
    test_pf1.attach(vm1_nic_uuid, vm1)
    test_pf2.attach(vm1_nic_uuid, vm1)

    vm1.start()
    time.sleep(50)
    vip.check()

    # pf_1_delete pf_2_delete
    test_pf1.delete()
    test_pf2.delete()
    
    
    # clean_up
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass("Test Port Forwarding Attach/Detach Successfully")

def error_cleanup():
    global vm1,vm2,vip
    vm1.destroy()
    vm2.destroy()
    vm1.expunge()
    vm2.expunge()
