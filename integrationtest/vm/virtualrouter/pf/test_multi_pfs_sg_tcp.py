'''

Test 2 port forwarding with same vip, but assign to different vm_nics of 
different VMs. Also will test with SG.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as zstack_sg_vm_header
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import apibinding.inventory as inventory

import os

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
PfRule = test_state.PfRule
Port = test_state.Port

test_obj_dict = test_state.TestStateDict()
eip_snatInboundTraffic_default_value = None
pf_snatInboundTraffic_default_value = None

def test():
    '''
        Since VR ip address is assigned by zstack, so we need to use VR to test
        PF rules' connectibility. 

        PF test needs at least 3 VR existence. The PF VM's VR is for set PF 
        rule. The PF rule will add VIP for PF_VM. Besides of PF_VM's VR, there 
        are needed another 2 VR VMs. 1st VR public IP address will be set as 
        allowedCidr. The 1st VR VM should be able to access PF_VM. So the 2nd VR
        VM should not be able to access PF_VM.

        In this test, will also add SG rules to check the coexistence between
        PF and SG. SG rule will be added onto PF_VM's internal IP.
    '''
    global eip_snatInboundTraffic_default_value
    global pf_snatInboundTraffic_default_value
    #enable snatInboundTraffic and save global config value
    eip_snatInboundTraffic_default_value = \
            conf_ops.change_global_config('eip', 'snatInboundTraffic', 'false')
    pf_snatInboundTraffic_default_value = \
            conf_ops.change_global_config('portForwarding', \
            'snatInboundTraffic', 'false')
    pf_vm1 = test_stub.create_dnat_vm()
    test_obj_dict.add_vm(pf_vm1)
    pf_vm2 = test_stub.create_dnat_vm()
    test_obj_dict.add_vm(pf_vm2)

    l3_name = os.environ.get('l3VlanNetworkName1')
    vr1 = test_stub.create_vr_vm(test_obj_dict, l3_name)

    l3_name = os.environ.get('l3NoVlanNetworkName1')
    vr2 = test_stub.create_vr_vm(test_obj_dict, l3_name)

    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    vr2_pub_ip = test_lib.lib_find_vr_pub_ip(vr2)
    
    pf_vm1.check()

    vm_nic1 = pf_vm1.vm.vmNics[0]
    vm_nic_uuid1 = vm_nic1.uuid
    pri_l3_uuid = vm_nic1.l3NetworkUuid
    vm_nic2 = pf_vm2.vm.vmNics[0]
    vm_nic_uuid2 = vm_nic2.uuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip = test_stub.create_vip('pf_sg_test', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid

    pf_creation_opt1 = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule1_ports, private_target_rule=Port.rule1_ports, vip_uuid=vip_uuid, vm_nic_uuid=vm_nic_uuid1)
    test_pf1 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf1.set_creation_option(pf_creation_opt1)
    test_pf1.create(pf_vm1)
    vip.attach_pf(test_pf1)

    pf_creation_opt2 = PfRule.generate_pf_rule_option(vr2_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule2_ports, private_target_rule=Port.rule2_ports, vip_uuid=vip_uuid, vm_nic_uuid=vm_nic_uuid2)
    test_pf2 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf2.set_creation_option(pf_creation_opt2)
    test_pf2.create(pf_vm2)
    vip.attach_pf(test_pf2)

    pf_vm1.check()
    pf_vm2.check()
    vip.check()

    sg1 = test_stub.create_sg()
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg_vm = zstack_sg_vm_header.ZstackTestSgVm()
    sg_vm.check()

    vm_nics = (vm_nic_uuid1, pf_vm1)
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vr1_pub_ip)
    rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vr2_pub_ip)
    sg1.add_rule([rule1])

    test_util.test_dsc("Add nic to security group 1.")
    test_util.test_dsc("PF1 rule is allowed, since VR1's IP is granted by SG Rule1. PF2 rule is allowed, since VM2's ip is not controlld by SG.")
    sg_vm.attach(sg1, [vm_nics])
    vip.check()

    test_util.test_dsc("Remove rule1 from security group 1.")
    test_util.test_dsc("PF rules are still allowed")
    sg1.delete_rule([rule1])
    vip.check()

    test_util.test_dsc("Add rule2")
    test_util.test_dsc("PF1 rule is not allowed, since SG rule2 only allowed the ingress from VR2, but VR2 can't pass PF rule. PF2 rule is still allowed, since its vmnic is not controlled by SG.")
    sg1.add_rule([rule2])
    vip.check()

    test_util.test_dsc("Delete SG")
    sg_vm.delete_sg(sg1)
    test_util.test_dsc("All PFs rule are allowed")
    vip.check()

    test_pf1.delete()
    test_pf2.delete()
    pf_vm1.destroy()
    test_obj_dict.rm_vm(pf_vm1)
    pf_vm2.destroy()
    test_obj_dict.rm_vm(pf_vm2)

    vip.delete()
    test_obj_dict.rm_vip(vip)
    conf_ops.change_global_config('eip', 'snatInboundTraffic', \
            eip_snatInboundTraffic_default_value )
    conf_ops.change_global_config('portForwarding', 'snatInboundTraffic', \
            pf_snatInboundTraffic_default_value)
    test_util.test_pass("Test 2 Port Forwarding Rules with same VIP assigned to different vmnic  Successfully.")

#Will be called only if exception happens in test().
def error_cleanup():
    global eip_snatInboundTraffic_default_value
    global pf_snatInboundTraffic_default_value
    conf_ops.change_global_config('eip', 'snatInboundTraffic', \
            eip_snatInboundTraffic_default_value )
    conf_ops.change_global_config('portForwarding', 'snatInboundTraffic', \
            pf_snatInboundTraffic_default_value)
    test_lib.lib_error_cleanup(test_obj_dict)
