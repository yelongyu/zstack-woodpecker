'''

Test shared Security Group for 5 VMs with both ingress and exgress connection

2 VMs in Group1
2 Vms in Group2
1 VM is alone

All VMs will be granted 0~100 port ingress and egress, this will make sure VR VM could connect (ssh) to each VM to do port checking

Will setup both ingress/egress rules for Group1. 

As Group2 VMs have been add 0~100 ingress/egress permission, they will not able to connect to Group1 VMs besides of 0~100 ports, unless more rules will be added to Group2. 

This test case will also check providing an Group1 VM ipaddr as egress target and make sure another VM (from Group1) will not be accessible. 

This case doesn't depend on stub_vm to do the testing. So it can't only rely on sg_vm.check() to do the validation. Has to do the validation by itself.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory

_config_ = {
        'timeout' : 2000
        }

test_stub = test_lib.lib_get_test_stub()
Port = test_state.Port

test_obj_dict = test_state.TestStateDict()

def test():
    '''
        Test image requirements:
            1. have nc to check the network port
            2. have "nc" to open any port
            3. it doesn't include a default firewall
        VR image is a good candiate to be the guest image.
    '''
    test_util.test_dsc("Create 3 VMs with vlan VR L3 network and using VR image.")
    vm1 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm2)
    vm3 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm3)
    vm4 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm4)
    vm5 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm5)
    vm1.check()
    vm2.check()
    vm3.check()
    vm4.check()
    vm5.check()

    test_util.test_dsc("Create security groups.")
    sg1 = test_stub.create_sg()
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg2 = test_stub.create_sg()
    test_obj_dict.add_sg(sg2.security_group.uuid)
    sg3 = test_stub.create_sg()
    test_obj_dict.add_sg(sg3.security_group.uuid)
    sg4 = test_stub.create_sg()
    test_obj_dict.add_sg(sg4.security_group.uuid)
    sg5 = test_stub.create_sg()
    test_obj_dict.add_sg(sg5.security_group.uuid)
    sg_vm = test_sg_vm_header.ZstackTestSgVm()
    sg_vm.check()

    vr_vm = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vr_internal_ip = test_lib.lib_find_vr_private_ip(vr_vm)
    vm1_ip = vm1.vm.vmNics[0].ip
    vm2_ip = vm2.vm.vmNics[0].ip
    vm3_ip = vm3.vm.vmNics[0].ip
    vm4_ip = vm4.vm.vmNics[0].ip
    vm5_ip = vm5.vm.vmNics[0].ip

    l3_uuid = vm1.vm.vmNics[0].l3NetworkUuid
    nic_uuid1 = vm1.vm.vmNics[0].uuid
    nic_uuid2 = vm2.vm.vmNics[0].uuid
    nic_uuid3 = vm3.vm.vmNics[0].uuid
    nic_uuid4 = vm4.vm.vmNics[0].uuid
    nic_uuid5 = vm5.vm.vmNics[0].uuid
    vm1_nics = (nic_uuid1, vm1)
    vm2_nics = (nic_uuid2, vm2)
    vm3_nics = (nic_uuid3, vm3)
    vm4_nics = (nic_uuid4, vm4)
    vm5_nics = (nic_uuid5, vm5)
    vm_group1_nics = [vm1_nics, vm2_nics]
    vm_group2_nics = [vm3_nics, vm4_nics]
    #vms_nics = vm_group1_nics + vm_group1_nics + [vm5_nics]
    vms_nics = vm_group1_nics + vm_group2_nics

    test_util.test_dsc("Open some ports in 5 VMs for testing.")
    for vm in vm1,vm2,vm3,vm4,vm5:
        test_lib.lib_open_vm_listen_ports(vm.vm, test_stub.target_ports)
    
    rule_ai1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vr_internal_ip)
    rule_ae1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.EGRESS, vm5_ip)
    rule_v3i_2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vm3_ip)
    rule_v3e_2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.EGRESS, vm3_ip)

    rule_v3e_3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.EGRESS, vm3_ip)
    rule_v3i_3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.INGRESS, vm3_ip)
    rule_v4i_2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vm4_ip)
    rule_v4e_2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.EGRESS, vm4_ip)
    rule_v1i_2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vm1_ip)
    rule_v1e_2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.EGRESS, vm1_ip)
    rule_v2i_2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vm2_ip)
    rule_v2e_2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.EGRESS, vm2_ip)
    rule_v1i_3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.INGRESS, vm1_ip)
    rule_v1e_3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.EGRESS, vm1_ip)
    
    sg1.add_rule([rule_ai1, rule_ae1])
    sg2.add_rule([rule_v3i_2, rule_v4i_2, rule_v3e_2, rule_v4e_2])
    sg3.add_rule([rule_v1i_2, rule_v2i_2, rule_v1e_2, rule_v2e_2])
    sg4.add_rule([rule_v1i_3, rule_v1e_3])
    sg5.add_rule([rule_v3e_3, rule_v3i_3])

    sg_vm.add_stub_vm(l3_uuid, vm5)
    sg_vm.check()
    
    ##add all vm1 vm2 vm3 vm4 vm5 to sg1.
    test_util.test_dsc("Add all VMs to security group 1.")
    test_util.test_dsc("Allowed ingress and egress [ports:] %s" % test_stub.rule1_ports)
    sg_vm.attach(sg1, vms_nics)
    
    #add vm1 vm2 to SG2.
    test_util.test_dsc("Add VM1 and VM2 to SG2.")
    test_util.test_dsc("Allowed ingress [ports:] %s from VM3 and VM4" % test_stub.rule2_ports)
    test_util.test_dsc("Allowed egress [ports:] %s to VM3 and VM4" % test_stub.rule2_ports)
    test_util.test_dsc("Since VM1/VM2 are in same SG group, VM1/VM2 can connect rule2 ports :%s each other." % test_stub.rule2_ports)
    sg_vm.attach(sg2, vm_group1_nics)
    sg_vm.check()
    test_util.test_dsc("Since VM3/VM4 didn't open rule2 ports for VM1/VM2, VM1/VM2 can't connect to VM3/VM4 rule2 ports :%s." % test_stub.rule2_ports)
    test_lib.lib_check_vm_ports(vm3.vm, vm1.vm, test_stub.rule1_ports, (test_stub.rule2_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))
    test_lib.lib_check_vm_ports(vm3.vm, vm2.vm, test_stub.rule1_ports, (test_stub.rule2_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))
    test_lib.lib_check_vm_ports(vm4.vm, vm1.vm, test_stub.rule1_ports, (test_stub.rule2_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))
    test_lib.lib_check_vm_ports(vm4.vm, vm2.vm, test_stub.rule1_ports, (test_stub.rule2_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))

    test_lib.lib_check_vm_group_ports(vm1.vm, [vm3.vm, vm4.vm], test_stub.rule1_ports, (test_stub.rule2_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))
    test_util.test_dsc("Add rule2 ports to VM3 and VM4.")
    test_util.test_dsc("Allowed ingress [ports:] %s from VM1/VM2 to VM3/VM4" % (test_stub.rule1_ports + test_stub.rule2_ports))
    test_util.test_dsc("Allowed egress [ports:] %s to VM1 and VM2" % test_stub.rule2_ports)
    sg_vm.attach(sg3, vm_group2_nics)
    test_lib.lib_check_vm_group_ports(vm4.vm, [vm1.vm, vm2.vm], (test_stub.rule1_ports + test_stub.rule2_ports), (test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))
    test_lib.lib_check_vm_group_ports(vm2.vm, [vm3.vm, vm4.vm], (test_stub.rule1_ports + test_stub.rule2_ports), (test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))
    sg_vm.check()
    
    test_util.test_dsc("Add VM3 and VM4 to SG4.")
    test_util.test_dsc("Allowed ingress/egress [ports:] %s for VM1" % test_stub.rule3_ports)
    test_util.test_dsc("But due to VM1 didn't open related ports, connection will be denied for [ports:] %s from VM1 to VM3 " % test_stub.rule3_ports)
    test_util.test_dsc("The enabled connections for VM1/VM3 are still [ports:] %s " % (test_stub.rule1_ports + test_stub.rule2_ports))
    sg_vm.attach(sg4, vm_group2_nics)
    test_lib.lib_check_vm_ports(vm1.vm, vm3.vm, (test_stub.rule1_ports + test_stub.rule2_ports), (test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))
    test_util.test_dsc("As VM3/VM4 are in same SG group, rule1+rule2+rule3 [ports:] %s are opened between VM4 and VM3 " % (test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports))
    sg_vm.check()

    test_util.test_dsc("Add VM1 and VM2 to SG5.")
    test_util.test_dsc("Allowed ingress/egress [ports:] %s for VM3" % test_stub.rule3_ports)
    test_util.test_dsc("Connection between VM1 and VM3, between VM1 and VM2, between VM3 and VM4 are enabled for [ports:] %s" % (test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports))
    sg_vm.attach(sg5, vm_group1_nics)
    test_lib.lib_check_vm_ports(vm1.vm, vm3.vm, (test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports), (test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))
    test_lib.lib_check_vm_ports(vm3.vm, vm1.vm, (test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports), (test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))
    test_lib.lib_check_vm_ports(vm4.vm, vm3.vm, (test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports), (test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))

    test_util.test_dsc("Connection from VM2 to VM3 are enabled for [ports:]" % (test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports))
    test_lib.lib_check_vm_ports(vm2.vm, vm3.vm, (test_stub.rule1_ports + test_stub.rule2_ports), (test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))
    test_lib.lib_check_vm_ports(vm4.vm, vm2.vm, (test_stub.rule1_ports + test_stub.rule2_ports), (test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))

    #test_util.test_dsc("VM5 was not granted with rule2 and rule3 ports, so only rule1 [ports:] %s are allowned to connect to other VMs." % test_stub.rule1_ports)
    #test_lib.lib_check_vm_ports(vm5.vm, vm3.vm, test_stub.rule1_ports, (test_stub.rule2_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports + test_stub.denied_ports))

    #clean up.
    for sg in sg1,sg2,sg3,sg4,sg5:
        sg_vm.delete_sg(sg)
        test_obj_dict.rm_sg(sg.security_group.uuid)

    for vm in vm1,vm2,vm3,vm4,vm5:
        vm.destroy()
        test_obj_dict.rm_vm(vm)

    test_util.test_pass('Security Group Vlan VirtualRouter VM complex testing with 2 Groups 5 VMs Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
