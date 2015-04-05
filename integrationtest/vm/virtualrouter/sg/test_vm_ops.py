'''

Test Security Group for 1 VM with ingress rules and VM operations: shutdown, start, reboot and destroy. Will check if VM SG rules are still there, after vm operations.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory
import zstacklib.utils.linux as linux

test_stub = test_lib.lib_get_test_stub()
Port = test_state.Port

test_obj_dict = test_state.TestStateDict()

def do_check(params):
    vm = params[0]
    special_str = params[1]
    if test_lib.lib_check_vm_sg_rule_exist_in_iptables(vm, special_string=special_str):
        test_util.test_logger('[vm:] %s SG INGRESS rules are not removed, after it is destroyed. Will try again.' % vm.uuid)
        return False
    return True

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
    
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vm2_ip)
    rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vm2_ip)
    rule3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.INGRESS, vm2_ip)
    rule4 = test_lib.lib_gen_sg_rule(Port.rule4_ports, inventory.TCP, inventory.INGRESS, vm2_ip)
    rule5 = test_lib.lib_gen_sg_rule(Port.rule5_ports, inventory.TCP, inventory.INGRESS, vm2_ip)

    sg1.add_rule([rule1])
    sg2.add_rule([rule1, rule2, rule3])
    sg3.add_rule([rule3, rule4, rule5])
    sg_vm.check()

    sg_vm.add_stub_vm(l3_uuid, vm2)

    #test_util.test_dsc("Create SG rule6: allow connection from vr to port 0~65535")
    #rule6 = inventory.SecurityGroupRuleAO()
    #rule6.allowedCidr = '%s/32' % vr_internal_ip
    #rule6.protocol = inventory.TCP
    #rule6.startPort = 0 
    #rule6.endPort = 65535
    #rule6.type = inventory.INGRESS

    #test_stub.lib_add_sg_rules(sg1.uuid, [rule1, rule6])
    
    #add sg1
    test_util.test_dsc("Attach security group 1 to [nic:] %s L3." % nic_uuid)
    test_util.test_dsc("Add nic to security group 1.")
    sg_vm.attach(sg1, [vm_nics])
    sg_vm.check()
    
    #add sg2
    test_util.test_dsc("Attach security group 2 to [nic:] %s L3." % nic_uuid)
    test_util.test_dsc("Add nic to security group 2.")
    sg_vm.attach(sg2, [vm_nics])
    sg_vm.check()

    #add sg3
    test_util.test_dsc("Attach security group 3 to [nic:] %s L3." % nic_uuid)
    test_util.test_dsc("Add nic to security group 3.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports
    test_util.test_dsc("Allowed ports: %s" % tmp_allowed_ports)
    sg_vm.attach(sg3, [vm_nics])
    sg_vm.check()

    #shutdown vm1
    test_util.test_dsc("Shutdown VM1")
    vm1.stop()
    sg_vm.check()

    test_util.test_dsc("Start VM1")
    vm1.start()
    vm1.check()
    
    test_util.test_dsc("Allowed ports: %s" % tmp_allowed_ports)
    sg_vm.check()

    test_util.test_dsc("Restart VM1")
    vm1.reboot()
    vm1.check()
    
    test_util.test_dsc("Allowed ports: %s" % tmp_allowed_ports)
    sg_vm.check()

    test_util.test_dsc("Destroy VM1. All its SG rules should be removed.")
    vm_internalId = test_lib.lib_get_vm_internal_id(vm1.vm)
    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    if linux.wait_callback_success(do_check, (vm1.vm, "vnic%s.0-in" % vm_internalId), 5, 0.2):
        test_util.test_logger('[vm:] %s SG INGRESS rules are removed, after it is destroyed.' % vm1.vm.uuid)
    else:
        test_util.test_fail('[vm:] %s SG INGRESS rules are not removed, after it is destroyed 5 seconds. ' % vm1.vm.uuid)

    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    sg_vm.delete_sg(sg3)
    test_obj_dict.rm_sg(sg3.security_group.uuid)
    sg_vm.delete_sg(sg2)
    test_obj_dict.rm_sg(sg2.security_group.uuid)
    sg_vm.delete_sg(sg1)
    test_obj_dict.rm_sg(sg1.security_group.uuid)
    test_util.test_pass('Security Group Vlan VirtualRouter VM Start/Stop/Reboot/Destroy Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
