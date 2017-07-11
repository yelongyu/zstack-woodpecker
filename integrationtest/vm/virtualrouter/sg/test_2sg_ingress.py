'''

Test shared Security Group for 2 VMs with ingress connection

@author: Glody
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
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
    vm1_ip = vm1.vm.vmNics[0].ip
    vm2 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm2)
    vm2_ip = vm2.vm.vmNics[0].ip
    vm1.check()
    vm2.check()

    test_util.test_dsc("Create security groups.")
    sg1 = test_stub.create_sg()
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg2 = test_stub.create_sg()
    test_obj_dict.add_sg(sg2.security_group.uuid)
    sg_vm = test_sg_vm_header.ZstackTestSgVm()
    sg_vm.check()

    l3_uuid = vm1.vm.vmNics[0].l3NetworkUuid
    vm1_nic_uuid = vm1.vm.vmNics[0].uuid
    vm2_nic_uuid = vm2.vm.vmNics[0].uuid

    #Attach security group to l3 network
    net_ops.attach_security_group_to_l3(sg1.security_group.uuid, l3_uuid)
    net_ops.attach_security_group_to_l3(sg2.security_group.uuid, l3_uuid)

    #Add vm1 nic to security group
    sg_vm.attach(sg1, [(vm1_nic_uuid, vm1)])
    sg_vm.check()
    sg_vm.attach(sg2, [(vm2_nic_uuid, vm2)])
    sg_vm.check()

    rule1_1 = test_lib.lib_gen_sg_rule(Port.icmp_ports, inventory.ICMP, inventory.INGRESS, vm2_ip)
    rule1_2 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vm2_ip)
    rule1_3 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.UDP, inventory.INGRESS, vm2_ip)
    sg1.add_rule([rule1_1,rule1_2,rule1_3], [sg2.security_group.uuid])
    sg_vm.check()
    sg_vm.add_stub_vm(l3_uuid, vm2)
    sg_vm.check()
    sg_vm.delete_stub_vm(l3_uuid)

    rule2_1 = test_lib.lib_gen_sg_rule(Port.icmp_ports, inventory.ICMP, inventory.INGRESS, vm1_ip)
    rule2_2 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vm1_ip)
    rule2_3 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.UDP, inventory.INGRESS, vm1_ip)
    sg2.add_rule([rule2_1,rule2_2,rule2_3], [sg1.security_group.uuid])
    sg_vm.check()
    sg_vm.add_stub_vm(l3_uuid, vm1)
    #sg_vm.check()
    try:
        test_lib.lib_open_vm_listen_ports(vm1.vm, Port.ports_range_dict['rule1_ports'], l3_uuid)
        test_lib.lib_open_vm_listen_ports(vm2.vm, Port.ports_range_dict['rule1_ports'], l3_uuid)
        test_lib.lib_check_vm_ports_in_a_command(vm1.vm, vm2.vm, Port.ports_range_dict['rule1_ports'], [])
    except:
        test_util.test_fail('Security Group Meets Failure When Checking Ingress Rule. ')

    #Cleanup
    sg_vm.delete_sg(sg2)
    test_obj_dict.rm_sg(sg2.security_group.uuid)
    sg_vm.delete_sg(sg1)
    test_obj_dict.rm_sg(sg1.security_group.uuid)
    sg_vm.check()
    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    test_util.test_pass('Security Group Vlan VirtualRouter 2 VMs Group Ingress Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
