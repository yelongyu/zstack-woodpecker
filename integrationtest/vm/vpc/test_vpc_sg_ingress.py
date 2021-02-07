'''

Test Security Group for 1 VM with ingress connection control

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory
from itertools import izip


VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork2"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]
SECOND_PUB = 'l3NoVlanNetworkName1'

vpc1_l3_list = [VLAN1_NAME, VLAN2_NAME, SECOND_PUB]
vpc2_l3_list = [VXLAN1_NAME, VXLAN2_NAME, SECOND_PUB]

vpc_l3_list = [vpc1_l3_list, vpc2_l3_list]
vpc_name_list = ['vpc1', 'vpc2']

test_stub = test_lib.lib_get_test_stub()
Port = test_state.Port

test_obj_dict = test_state.TestStateDict()
vr_list = []


def test():
    '''
        Test image requirements:
            1. have nc to check the network port
            2. have "nc" to open any port
            3. it doesn't include a default firewall
        VR image is a good candiate to be the guest image.
    '''

    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(VLAN1_NAME, VLAN2_NAME))
    vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(VLAN1_NAME), l3_name=VLAN1_NAME)
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(VLAN2_NAME), l3_name=VLAN2_NAME)
    test_obj_dict.add_vm(vm2)
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
    l3_uuid = vm2.vm.vmNics[0].l3NetworkUuid

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

    test_util.test_dsc("Add nic to security group 1.")
    test_util.test_dsc("Allowed ports: %s" % Port.get_ports(Port.rule1_ports))
    sg_vm.attach(sg1, [vm_nics])
    sg_vm.check()

    test_util.test_dsc("Remove nic from security group 1.")
    sg_vm.detach(sg1, nic_uuid)
    sg_vm.check()

    test_util.test_dsc("Remove rule1 from security group 1.")
    sg1.delete_rule([rule1])
    sg_vm.check()

    test_util.test_dsc("Add rule1, rule2, rule3 to security group 1.")
    test_util.test_dsc("Allowed ports: %s" % test_stub.target_ports)
    sg1.add_rule([rule1, rule2, rule3])
    sg_vm.check()

    test_util.test_dsc("Add nic to security group 1 again.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports
    test_util.test_dsc("Allowed ports: %s" % tmp_allowed_ports)
    sg_vm.attach(sg1, [vm_nics])
    sg_vm.check()
    
    test_util.test_dsc("Remove rule2/3 from security group 1.")
    test_util.test_dsc("Allowed ports: %s" % test_stub.rule1_ports)
    sg1.delete_rule([rule2, rule3])
    sg_vm.check()
    
    test_util.test_dsc("Add rule2, rule3 back to security group 1.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports
    test_util.test_dsc("Allowed ports: %s" % tmp_allowed_ports)
    sg1.add_rule([rule2, rule3])
    sg_vm.check()

    test_util.test_dsc("Remove rule2/3 from security group 1.")
    test_util.test_dsc("Allowed ports: %s" % test_stub.rule1_ports)
    sg1.delete_rule([rule2, rule3])
    sg_vm.check()
    
    #add sg2
    test_util.test_dsc("Add nic to security group 2.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports
    test_util.test_dsc("Allowed ports: %s" % tmp_allowed_ports)
    sg_vm.attach(sg2, [vm_nics])
    sg_vm.check()

    #add sg3
    test_util.test_dsc("Add nic to security group 3.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports
    test_util.test_dsc("Allowed ports (rule1+rule2+rul3+rule4+rule5): %s" % tmp_allowed_ports)
    sg_vm.attach(sg3, [vm_nics])
    sg_vm.check()

    #detach nic from sg2
    test_util.test_dsc("Remove security group 2 for nic.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports
    test_util.test_dsc("Allowed ports (rule1+rule3+rule4+rule5): %s" % tmp_allowed_ports)
    sg_vm.detach(sg2, nic_uuid)
    sg_vm.check()

    #delete sg3
    test_util.test_dsc("Delete security group 3.")
    test_util.test_dsc("Allowed ports (rule1): %s" % test_stub.rule1_ports)
    sg_vm.delete_sg(sg3)
    sg_vm.check()
    test_obj_dict.rm_sg(sg3.security_group.uuid)

    #Cleanup
    sg_vm.delete_sg(sg2)
    test_obj_dict.rm_sg(sg2.security_group.uuid)
    sg_vm.delete_sg(sg1)
    test_obj_dict.rm_sg(sg1.security_group.uuid)
    sg_vm.check()
    vm1.check()
    vm2.check()
    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    test_util.test_pass('Security Group Vlan VirtualRouter VMs Test Success')

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
