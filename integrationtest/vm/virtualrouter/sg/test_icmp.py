'''

The test will specially test add/remove SG rules to stopped VM. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory

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
    global test_obj_dict
    test_util.test_dsc("Create 2 VMs with vlan VR L3 network and using VR image.")
    vm1 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm2)
    vm1.check()
    vm2.check()

    test_util.test_dsc("Create security groups.")
    sg1 = test_stub.create_sg()
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg2 = test_stub.create_sg()
    test_obj_dict.add_sg(sg2.security_group.uuid)
    sg3 = test_stub.create_sg()
    test_obj_dict.add_sg(sg3.security_group.uuid)
    sg_vm = test_sg_vm_header.ZstackTestSgVm()
    sg_vm.check()

    nic_uuid = vm1.vm.vmNics[0].uuid
    vm_nics = (nic_uuid, vm1)
    l3_uuid = vm1.vm.vmNics[0].l3NetworkUuid

    vr_vm = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vm2_ip = test_lib.lib_get_vm_nic_by_l3(vm2.vm, l3_uuid).ip
    vr_internal_ip = test_lib.lib_find_vr_private_ip(vr_vm)
    
    test_util.test_dsc("Create SG rule1: allow connection to vm2 port 0~100")
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.EGRESS, vm2_ip)
    test_util.test_dsc("Create SG rule2: allow connection from vm2 to port 9000~10000")
    rule2 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.INGRESS, vm2_ip)
    test_util.test_dsc("Create SG rule3: allow connection from VR to port 0~65535 to make VR can connect VMs to do testing")
    rule3 = test_lib.lib_gen_sg_rule(Port.icmp_ports, inventory.ICMP, inventory.INGRESS, vr_internal_ip)
    test_util.test_dsc("Create SG rule4: allow ICMP connection to VR")
    rule4 = test_lib.lib_gen_sg_rule(Port.icmp_ports, inventory.ICMP, inventory.EGRESS, vr_internal_ip)

    test_util.test_dsc("Create SG rule5: allow icmp from vm2")
    rule5 = test_lib.lib_gen_sg_rule(Port.icmp_ports, inventory.ICMP, inventory.INGRESS, vm2_ip)
    
    test_util.test_dsc("Create SG rule6: allow icmp to vm2")
    rule6 = test_lib.lib_gen_sg_rule(Port.icmp_ports, inventory.ICMP, inventory.EGRESS, vm2_ip)

    sg1.add_rule([rule1, rule2, rule3, rule4])
    sg2.add_rule([rule5])
    sg3.add_rule([rule6])
    sg_vm.check()

    sg_vm.add_stub_vm(l3_uuid, vm2)

    sg_vm.check()
    
    #add sg1
    test_util.test_dsc("Add VM1 nic to security group 1.")
    sg_vm.attach(sg1, [vm_nics])
    sg_vm.check()
    
    if not test_lib.lib_check_ping(vm1.vm, vr_internal_ip, no_exception=True):
        test_util.test_fail('Exception: [vm:] %s ping [vr:] %s fail. But it should ping successfully.' % (vm1.vm.uuid, vr_internal_ip))

    #add sg2
    test_util.test_dsc("Add VM1 nic to security group 2.")
    sg_vm.attach(sg2, [vm_nics])
    test_util.test_dsc("Allowed ports egress rules1: %s, ingress rule2: %s" % (test_stub.rule1_ports, test_stub.rule2_ports))
    sg_vm.check()

    if not test_lib.lib_check_ping(vm1.vm, vr_internal_ip, no_exception=True):
        test_util.test_fail('Exception: [vm:] %s ping [vr:] %s fail. But it should ping successfully.' % (vm1.uuid, vr_internal_ip))

    #add sg3
    test_util.test_dsc("Add nic to security group 3 to stopped vm1.")
    sg_vm.attach(sg3, [vm_nics])
    test_util.test_dsc("Allowed ports egress rules1: %s, ingress rule2: %s" % (test_stub.rule1_ports, test_stub.rule2_ports))
    sg_vm.check()
    if not test_lib.lib_check_ping(vm1.vm, vr_internal_ip, no_exception=True):
        test_util.test_fail('Exception: [vm:] %s ping [vr:] %s fail. But it should ping successfully.' % (vm1.uuid, vr_internal_ip))

    test_util.test_dsc("remove rule5 from sg2")
    sg2.delete_rule([rule5])
    sg_vm.check()
    if not test_lib.lib_check_ping(vm1.vm, vr_internal_ip, no_exception=True):
        test_util.test_fail('Exception: [vm:] %s ping [vr:] %s fail. But it should ping successfully.' % (vm1.uuid, vr_internal_ip))


    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    
    sg_vm.check()
    sg1.delete()
    test_obj_dict.rm_sg(sg1.security_group.uuid)
    sg2.delete()
    test_obj_dict.rm_sg(sg2.security_group.uuid)

    sg_vm.check()
    sg3.delete()
    test_obj_dict.rm_sg(sg3.security_group.uuid)

    test_util.test_pass('Security Group Vlan VirtualRouter VM ICMP rules Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
