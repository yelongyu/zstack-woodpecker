'''

Test Port Forwarding with TCP connection and SG rule coexist

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
    vip = test_stub.create_vip('pf_sg_test', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid

    pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule1_ports, private_target_rule=Port.rule1_ports, vip_uuid=vip_uuid, vm_nic_uuid=vm_nic_uuid)
    test_pf = zstack_pf_header.ZstackTestPortForwarding()
    test_pf.set_creation_option(pf_creation_opt)
    test_pf.create(pf_vm)
    vip.attach_pf(test_pf)

    pf_vm.check()
    #Ignore this check, since it has been checked many times in other PF cases.
    #test_pf.check()
    sg1 = test_stub.create_sg()
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg_vm = zstack_sg_vm_header.ZstackTestSgVm()
    sg_vm.check()

    vm_nics = (vm_nic_uuid, pf_vm)
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vr1_pub_ip)
    rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vr2_pub_ip)
    sg1.add_rule([rule1])

    test_util.test_dsc("Add nic to security group 1.")
    test_util.test_dsc("PF rule is allowed, since VR1's IP is granted by SG Rule1.")
    sg_vm.attach(sg1, [vm_nics])
    vip.check()

    test_util.test_dsc("Remove rule1 from security group 1.")
    test_util.test_dsc("PF rule is still allowed")
    sg1.delete_rule([rule1])
    vip.check()

    test_util.test_dsc("Add rule2")
    test_util.test_dsc("PF rule is not allowed, since rule2 only allowed the ingress from VR2, but VR2 can't pass PF rule. ")
    sg1.add_rule([rule2])
    vip.check()

    test_util.test_dsc("Delete SG")
    sg_vm.delete_sg(sg1)
    test_util.test_dsc("PF rule is allowed")
    vip.check()

    pf_vm.destroy()
    test_obj_dict.rm_vm(pf_vm)
    vip.check()
    test_pf.delete()

    vip.delete()
    test_obj_dict.rm_vip(vip)
    conf_ops.change_global_config('eip', 'snatInboundTraffic', \
            eip_snatInboundTraffic_default_value )
    conf_ops.change_global_config('portForwarding', 'snatInboundTraffic', \
            pf_snatInboundTraffic_default_value)
    test_util.test_pass("Test Port Forwarding TCP Rule Successfully")

#Will be called only if exception happens in test().
def error_cleanup():
    global eip_snatInboundTraffic_default_value
    global pf_snatInboundTraffic_default_value
    conf_ops.change_global_config('eip', 'snatInboundTraffic', \
            eip_snatInboundTraffic_default_value )
    conf_ops.change_global_config('portForwarding', 'snatInboundTraffic', \
            pf_snatInboundTraffic_default_value)
    test_lib.lib_error_cleanup(test_obj_dict)
