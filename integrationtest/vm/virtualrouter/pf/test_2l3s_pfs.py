'''
    Test Description:
        Will create 1 VM with 2 l3 networks. Assign 2 vip and 2 pf to each l3.


@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import apibinding.inventory as inventory

import os

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

PfRule = test_state.PfRule
Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
eip_snatInboundTraffic_default_value = None
pf_snatInboundTraffic_default_value = None

def test():
    global eip_snatInboundTraffic_default_value
    global pf_snatInboundTraffic_default_value
    #enable snatInboundTraffic and save global config value
    eip_snatInboundTraffic_default_value = \
            conf_ops.change_global_config('eip', 'snatInboundTraffic', 'true')
    pf_snatInboundTraffic_default_value = \
            conf_ops.change_global_config('portForwarding', \
            'snatInboundTraffic', 'true')

    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list = [l3_net_uuid]
    l3_name = os.environ.get('l3VlanDNATNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list.append(l3_net_uuid)

    vm = test_stub.create_vm(l3_net_list, image_uuid, '2_l3_pf_vm')
    test_obj_dict.add_vm(vm)

    l3_name = os.environ.get('l3NoVlanNetworkName1')
    vr1 = test_stub.create_vr_vm(test_obj_dict, l3_name)
    if vr1.applianceVmType == "Vyos":
        test_util.test_skip("Vyos VR does not support single VM multiple VIP")

    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    
    vm.check()

    vm_nic1 = vm.vm.vmNics[0]
    vm_nic1_uuid = vm_nic1.uuid
    vm_nic2 = vm.vm.vmNics[1]
    vm_nic2_uuid = vm_nic2.uuid
    pri_l3_uuid = vm_nic1.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    if vr.applianceVmType == "Vyos":
        test_util.test_skip("Vyos VR does not support single VM multiple VIP")

    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip1 = test_stub.create_vip('vip1_2l3s_vm_test', l3_uuid)
    test_obj_dict.add_vip(vip1)
    vip1_uuid = vip1.get_vip().uuid
    vip2 = test_stub.create_vip('vip2_2l3s_vm_test', l3_uuid)
    test_obj_dict.add_vip(vip2)
    vip2_uuid = vip2.get_vip().uuid

    pf_creation_opt1 = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule4_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip1_uuid, vm_nic_uuid=vm_nic1_uuid)
    test_pf1 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf1.set_creation_option(pf_creation_opt1)
    test_pf1.create(vm)
    vip1.attach_pf(test_pf1)

    pf_creation_opt2 = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule5_ports, private_target_rule=Port.rule5_ports, vip_uuid=vip2_uuid, vm_nic_uuid=vm_nic2_uuid)
    test_pf2 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf2.set_creation_option(pf_creation_opt2)
    test_pf2.create(vm)
    vip2.attach_pf(test_pf2)

    vip1.check()
    vip2.check()

    vip1.delete()
    test_obj_dict.rm_vip(vip1)
    vip2.delete()
    test_obj_dict.rm_vip(vip2)
    vm.destroy()
    conf_ops.change_global_config('eip', 'snatInboundTraffic', \
            eip_snatInboundTraffic_default_value )
    conf_ops.change_global_config('portForwarding', 'snatInboundTraffic', \
            pf_snatInboundTraffic_default_value)
    test_util.test_pass('Create 1 VM with 2 l3_network with 2 VIP PF testing successfully.')

#Will be called only if exception happens in test().
def error_cleanup():
    global eip_snatInboundTraffic_default_value
    global pf_snatInboundTraffic_default_value
    conf_ops.change_global_config('eip', 'snatInboundTraffic', \
            eip_snatInboundTraffic_default_value )
    conf_ops.change_global_config('portForwarding', 'snatInboundTraffic', \
            pf_snatInboundTraffic_default_value)
    test_lib.lib_error_cleanup(test_obj_dict)
