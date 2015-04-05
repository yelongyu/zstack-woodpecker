'''

Test Migrate VM with PF and SG

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as zstack_sg_vm_header
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import apibinding.inventory as inventory

import os

test_stub = test_lib.lib_get_test_stub()
PfRule = test_state.PfRule
Port = test_state.Port

test_obj_dict = test_state.TestStateDict()

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
    pf_vm = test_stub.create_vr_vm('migrate_pf_sg_vm1', 'imageName_s', 'l3VlanNetwork2')
    test_obj_dict.add_vm(pf_vm)

    l3_name = os.environ.get('l3VlanNetworkName1')
    vr1_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr1_l3_uuid)
    temp_vm1 = None
    if not vrs:
        #create temp_vm1 for getting vlan1's vr for test pf_vm portforwarding
        temp_vm1 = test_stub.create_vr_vm('migrate_temp_vm1', 'imageName_s', 'l3VlanNetworkName1')
        test_obj_dict.add_vm(temp_vm1)
        vr1 = test_lib.lib_find_vr_by_vm(temp_vm1.vm)[0]
    else:
        vr1 = vrs[0]

    l3_name = os.environ.get('l3VlanNetwork3')
    vr2_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr2_l3_uuid)
    temp_vm2 = None
    if not vrs:
        #create temp_vm2 for getting novlan's vr for test pf_vm portforwarding
        temp_vm2 = test_stub.create_vr_vm('migrate_temp_vm2', 'imageName_s', 'l3VlanNetwork3')
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
    vip_option = test_util.VipOption()
    vip_option.set_l3_uuid(l3_uuid)
    vip_uuid = net_ops.create_vip(vip_option).uuid

    pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule1_ports, private_target_rule=Port.rule1_ports, vip_uuid=vip_uuid, vm_nic_uuid=vm_nic_uuid)
    test_pf = zstack_pf_header.ZstackTestPortForwarding()
    test_pf.set_creation_option(pf_creation_opt)
    test_pf.create(pf_vm)

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
    test_pf.check()

    test_stub.migrate_vm_to_random_host(pf_vm)

    test_util.test_dsc("Remove rule1 from security group 1.")
    test_util.test_dsc("PF rule is still allowed")
    sg1.delete_rule([rule1])
    test_pf.check()

    test_util.test_dsc("Add rule2")
    test_util.test_dsc("PF rule is not allowed, since rule2 only allowed the ingress from VR2, but VR2 can't pass PF rule. ")
    sg1.add_rule([rule2])
    test_pf.check()

    test_util.test_dsc("Delete SG")
    sg_vm.delete_sg(sg1)
    test_util.test_dsc("PF rule is allowed")
    test_pf.check()

    if temp_vm1:
        temp_vm1.destroy()
        test_obj_dict.rm_vm(temp_vm1)
    if temp_vm2:
        temp_vm2.destroy()
        test_obj_dict.rm_vm(temp_vm2)

    test_pf.delete()
    pf_vm.destroy()
    test_obj_dict.rm_vm(pf_vm)

    net_ops.delete_vip(vip_uuid)
    test_util.test_pass("Test Port Forwarding TCP Rule Successfully")

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
