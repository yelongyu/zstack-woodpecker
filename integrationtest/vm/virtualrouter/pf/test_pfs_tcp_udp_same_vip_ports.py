'''

Test Port Forwarding with multi rules connection(including TCP and UDP) within same vip.

TCP and UDP will share same ports. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
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
        PF test needs at least 3 VR existence. Besides of PF_VM's VR, there 
        are needed another 2 VR VMs. 1st VR public IP address will be set as 
        allowedCidr. The 1st VR VM should be able to access PF_VM. The 2nd VR
        VM should not be able to access PF_VM.
    '''
    global eip_snatInboundTraffic_default_value
    global pf_snatInboundTraffic_default_value
    #enable snatInboundTraffic and save global config value
    eip_snatInboundTraffic_default_value = \
            conf_ops.change_global_config('eip', 'snatInboundTraffic', 'true')
    pf_snatInboundTraffic_default_value = \
            conf_ops.change_global_config('portForwarding', \
            'snatInboundTraffic', 'true')

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
    vip = test_stub.create_vip('multi_rule_vip', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid

    pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, \
            protocol=inventory.TCP, \
            vip_target_rule=Port.rule1_ports, \
            private_target_rule=Port.rule1_ports, \
            vip_uuid=vip_uuid, \
            vm_nic_uuid=vm_nic_uuid)

    test_pf1 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf1.set_creation_option(pf_creation_opt)
    test_pf1.create(pf_vm)
    vip.attach_pf(test_pf1)
    vip.check()

    pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, \
            protocol=inventory.UDP, \
            vip_target_rule=Port.rule1_ports, \
            private_target_rule=Port.rule1_ports, \
            vip_uuid=vip_uuid, \
            vm_nic_uuid=vm_nic_uuid)

    test_pf2 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf2.set_creation_option(pf_creation_opt)
    test_pf2.create(pf_vm)
    vip.attach_pf(test_pf2)
    vip.check()

    pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, \
            protocol=inventory.UDP, \
            vip_target_rule=Port.rule2_ports, \
            private_target_rule=Port.rule2_ports, \
            vip_uuid=vip_uuid, \
            vm_nic_uuid=vm_nic_uuid)

    test_pf3 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf3.set_creation_option(pf_creation_opt)
    test_pf3.create(pf_vm)
    vip.attach_pf(test_pf3)
    vip.check()

    pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, \
            protocol=inventory.TCP, \
            vip_target_rule=Port.rule2_ports, \
            private_target_rule=Port.rule2_ports, \
            vip_uuid=vip_uuid, \
            vm_nic_uuid=vm_nic_uuid)

    test_pf4 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf4.set_creation_option(pf_creation_opt)
    test_pf4.create(pf_vm)
    vip.attach_pf(test_pf4)
    vip.check()

    pf_vm.check()

    test_pf1.delete()
    test_pf2.delete()
    test_pf3.delete()
    test_pf4.delete()
    vip.delete()
    test_obj_dict.rm_vip(vip)

    pf_vm.destroy()
    test_obj_dict.rm_vm(pf_vm)
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
