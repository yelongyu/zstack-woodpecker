'''

Test Deleting VIP before attach its Port Forwarding to any VM.

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

    vm_nic = pf_vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    pri_l3_uuid = vm_nic.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    vr_pub_ip = vr_pub_nic.ip
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip = test_stub.create_vip('delete_vip_before_attach_PF_to_VM', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid

    #pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule1_ports, private_target_rule=Port.rule1_ports)
    pf_creation_opt = PfRule.generate_pf_rule_option(vr_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule1_ports, private_target_rule=Port.rule1_ports, vip_uuid=vip_uuid)
    test_pf = zstack_pf_header.ZstackTestPortForwarding()
    test_pf.set_creation_option(pf_creation_opt)
    test_pf.create(pf_vm)
    vip.attach_pf(test_pf)

    vip.check()
    vip.delete()
    test_obj_dict.rm_vip(vip)

    pf_vm.destroy()
    test_obj_dict.rm_vm(pf_vm)

    test_util.test_pass("Test Delete VIP before attach Port Forwarding to any VM Successfully")

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
