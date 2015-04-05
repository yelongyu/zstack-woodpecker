'''

Test shared Security Group for 2 VMs with egress connection

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
    test_util.test_dsc("Create 3 VMs with vlan VR L3 network and using VR image.")
    vm1 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm2)
    vm3 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm3)
    vm1.check()
    vm2.check()
    vm3.check()

    test_util.test_dsc("Create security groups.")
    sg1 = test_stub.create_sg()
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg2 = test_stub.create_sg()
    test_obj_dict.add_sg(sg2.security_group.uuid)
    sg3 = test_stub.create_sg()
    test_obj_dict.add_sg(sg3.security_group.uuid)
    sg_vm = test_sg_vm_header.ZstackTestSgVm()
    sg_vm.check()

    l3_uuid = vm1.vm.vmNics[0].l3NetworkUuid

    vr_vm = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vm3_ip = test_lib.lib_get_vm_nic_by_l3(vm3.vm, l3_uuid).ip
    
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.EGRESS, vm3_ip)
    rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.EGRESS, vm3_ip)
    rule3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.EGRESS, vm3_ip)
    rule4 = test_lib.lib_gen_sg_rule(Port.rule4_ports, inventory.TCP, inventory.EGRESS, vm3_ip)
    rule5 = test_lib.lib_gen_sg_rule(Port.rule5_ports, inventory.TCP, inventory.EGRESS, vm3_ip)

    sg1.add_rule([rule1])
    sg2.add_rule([rule1, rule2, rule3])
    sg3.add_rule([rule3, rule4, rule5])
    sg_vm.add_stub_vm(l3_uuid, vm3)
    sg_vm.check()

    nic_uuid1 = vm1.vm.vmNics[0].uuid
    nic_uuid2 = vm2.vm.vmNics[0].uuid
    vm1_nics = (nic_uuid1, vm1)
    vm2_nics = (nic_uuid2, vm2)
    #vm_nics = [nic_uuid1, nic_uuid2]
    
    test_util.test_dsc("Add nic to security group 1.")
    test_util.test_dsc("Allowed egress ports: %s" % test_stub.rule1_ports)
    sg_vm.attach(sg1, [vm1_nics, vm2_nics])
    sg_vm.check()
    
    test_util.test_dsc("Remove nic from security group 1.")
    test_util.test_dsc("Allowed egress ports: %s" % test_stub.target_ports)
    sg_vm.detach(sg1, nic_uuid1)
    sg_vm.detach(sg1, nic_uuid2)
    sg_vm.check()
    
    test_util.test_dsc("Remove rule1 from security group 1.")
    sg1.delete_rule([rule1])
    test_util.test_dsc("Add nic to security group 1 again.")
    test_util.test_dsc("Allowed egress ports: %s" % test_stub.target_ports)
    sg_vm.attach(sg1, [vm1_nics, vm2_nics])
    sg_vm.check()
    
    test_util.test_dsc("Add rule1, rule2, rule3 to security group 1.")
    test_util.test_dsc("Allowed egress ports: %s" % test_stub.target_ports)
    sg1.add_rule([rule1, rule2, rule3])
    sg_vm.check()

    #can't directly remove rule1, as it will block vr ssh connection.
    test_util.test_dsc("Remove rule2/3 from security group 1.")
    test_util.test_dsc("Allowed egress ports: %s" % test_stub.rule1_ports)
    sg1.delete_rule([rule2, rule3])
    sg_vm.check()
    
    test_util.test_dsc("Add rule2, rule3 back to security group 1.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports
    test_util.test_dsc("Allowed egress ports: %s" % tmp_allowed_ports)
    sg1.add_rule([rule2, rule3])
    sg_vm.check()

    test_util.test_dsc("Remove rule2/3 from security group 1.")
    test_util.test_dsc("Allowed egress ports: %s" % test_stub.rule1_ports)
    sg1.delete_rule([rule2, rule3])
    sg_vm.check()
    
    #add sg2 to vm1
    test_util.test_dsc("Add vm 1 nic to security group 2.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports
    test_util.test_dsc("Allowed egress ports for vm1 to vm3: %s" % tmp_allowed_ports)
    sg_vm.attach(sg2, [vm1_nics])
    sg_vm.check()

    #add sg2 to vm2
    test_util.test_dsc("Add vm 2 nic to security group 2.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports
    test_util.test_dsc("Allowed egress ports for vm1 and vm2: %s" % tmp_allowed_ports)
    sg_vm.attach(sg2, [vm2_nics])
    sg_vm.check()

    #add sg3
    test_util.test_dsc("Add nic to security group 3.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports
    test_util.test_dsc("Allowed egress ports: %s" % tmp_allowed_ports)
    sg_vm.attach(sg3, [vm1_nics, vm2_nics])
    sg_vm.check()

    #remove sg2
    test_util.test_dsc("Remove security group 2 for nic.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports
    test_util.test_dsc("Allowed egress ports: %s" % tmp_allowed_ports)
    sg_vm.detach(sg2, nic_uuid1)
    sg_vm.detach(sg2, nic_uuid2)
    sg_vm.check()

    #delete sg3
    test_util.test_dsc("Delete security group 3.")
    test_util.test_dsc("Allowed ports: %s" % test_stub.rule1_ports)
    sg3.delete()
    test_obj_dict.rm_sg(sg3.security_group.uuid)
    sg_vm.check()

    sg_vm.delete_sg(sg2)
    test_obj_dict.rm_sg(sg2.security_group.uuid)
    sg_vm.delete_sg(sg1)
    test_obj_dict.rm_sg(sg1.security_group.uuid)
    sg_vm.check()
    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    vm3.destroy()
    test_obj_dict.rm_vm(vm3)
    test_util.test_pass('Security Group Vlan VirtualRouter 2 VMs Group Egress Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
