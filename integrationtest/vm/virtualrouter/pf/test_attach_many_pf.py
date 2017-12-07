'''

Test Attach/Detach many Port Forwarding

@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import zstackwoodpecker.operations.net_operations as net_ops
import apibinding.inventory as inventory

import os
import datetime

PfRule = test_state.PfRule
Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
pf_dict = {}

def test():
    pf_vm1 = test_stub.create_dnat_vm()
    test_obj_dict.add_vm(pf_vm1)

    l3_name = os.environ.get('l3VlanNetworkName1')
    vr1 = test_stub.create_vr_vm(test_obj_dict, l3_name)

    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    
    pf_vm1.check()

    vm_nic1 = pf_vm1.vm.vmNics[0]
    vm_nic_uuid1 = vm_nic1.uuid
    pri_l3_uuid = vm_nic1.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip = test_stub.create_vip('pf_attach_test', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid

    test_util.test_dsc("attach, detach and delete pf for many times")
    for i in range(1, 451):
        test_util.test_logger('round %s' % (i))
        starttime = datetime.datetime.now()
        pf_creation_opt1 = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule5_ports, private_target_rule=Port.rule5_ports, vip_uuid=vip_uuid)
        pf_creation_opt1.set_vip_ports(i, i)
        pf_creation_opt1.set_private_ports(i, i)
        test_pf1 = zstack_pf_header.ZstackTestPortForwarding()
        test_pf1.set_creation_option(pf_creation_opt1)
        test_pf1.create()
        vip.attach_pf(test_pf1)

        if i < 151:
            test_pf1.attach(vm_nic_uuid1, pf_vm1)
            pf_dict[i] = test_pf1.get_port_forwarding().uuid
        elif i < 301:
            test_pf1.attach(vm_nic_uuid1, pf_vm1)
            test_pf1.detach()
            pf_dict[i] = test_pf1.get_port_forwarding().uuid
        else :
            test_pf1.attach(vm_nic_uuid1, pf_vm1)
            test_pf1.detach()
            test_pf1.delete()
            
        endtime = datetime.datetime.now()
        optime = (endtime - starttime).seconds
        test_util.test_dsc("round %s, pf operation time: %s" % (i, optime))
        test_util.test_logger("the pf operation time is %s seconds" % optime)   
        if optime > 240:
            test_util.test_fail("the pf operation time is %s seconds, more than 240 seconds" % optime)   
  
    vip.delete()
    test_obj_dict.rm_vip(vip)
    pf_vm1.destroy()
    test_obj_dict.rm_vm(pf_vm1)
    for j in pf_dict:
        net_ops.delete_port_forwarding(pf_dict[j])

    test_util.test_pass("Test Port Forwarding Attach/Detach Successfully")

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    global pf_dict
    test_lib.lib_error_cleanup(test_obj_dict)
    for j in pf_dict:
        net_ops.delete_port_forwarding(pf_dict[j])
