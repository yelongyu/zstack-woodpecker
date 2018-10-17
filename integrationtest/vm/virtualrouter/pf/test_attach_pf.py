'''

Test Attach/Detach Port Forwarding

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import zstackwoodpecker.operations.config_operations as conf_ops
import apibinding.inventory as inventory

import os

PfRule = test_state.PfRule
Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    try:
        conf_ops.change_global_config('virtualRouter', 'ssh.passwordAuth', 'true')
    except:
        test_lib.test_logger('No global config ssh.passwordAuth')
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
    pf_vm2.check()

    vm_nic1 = pf_vm1.vm.vmNics[0]
    vm_nic_uuid1 = vm_nic1.uuid
    vm_nic2 = pf_vm2.vm.vmNics[0]
    vm_nic_uuid2 = vm_nic2.uuid
    pri_l3_uuid = vm_nic1.l3NetworkUuid
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

    pf_vm1.check()
    vip.check()

    test_pf1.attach(vm_nic_uuid1, pf_vm1)
    test_pf2.attach(vm_nic_uuid2, pf_vm2)
    vip.check()

    pf_vm1.stop()
    vip.check()

    test_pf1.detach()
    test_pf1.attach(vm_nic_uuid2, pf_vm2)
    pf_vm1.start()
    pf_vm1.check()
    vip.check()

    pf_vm1.stop()
    test_pf1.detach()
    test_pf2.detach()
    test_pf1.attach(vm_nic_uuid1, pf_vm1)
    test_pf2.attach(vm_nic_uuid1, pf_vm1)
    pf_vm1.start()
    pf_vm1.check()
    vip.check()

    vip.delete()
    test_obj_dict.rm_vip(vip)
    pf_vm1.destroy()
    test_obj_dict.rm_vm(pf_vm1)
    pf_vm2.destroy()
    test_obj_dict.rm_vm(pf_vm2)

    test_util.test_pass("Test Port Forwarding Attach/Detach Successfully")

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
