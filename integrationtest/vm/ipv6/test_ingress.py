'''

Test Security Group for 1 VM with egress connection control

@author: Pengtao.Zhang
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory
import zstacklib.utils.ssh as ssh
import os
import time

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
    test_util.test_dsc("Create 2 VMs with IPv6 L3 network and using VR image.")
    image_name = os.environ.get('ipv6ImageName')
    vm1 = test_stub.create_vm(l3_name = "%s,%s" %(os.environ.get('l3PublicNetworkName1'), os.environ.get('l3PublicNetworkName')), vm_name = 'IPv6 2 stack test ipv4 and ipv6', image_name = image_name)
    vm2 = test_stub.create_vm(l3_name = os.environ.get('l3PublicNetworkName1'), vm_name = 'IPv6 2 stack test ipv6', image_name = image_name)
    time.sleep(60) #waiting for vm bootup
    vm1_nic1 = vm1.get_vm().vmNics[0].ip
    vm1_nic2 = vm1.get_vm().vmNics[1].ip
    vm2_nic1 = vm2.get_vm().vmNics[0].ip
    for ip in (vm1_nic1, vm1_nic2):
        if "." in ip:
            ipv4 = ip
    print "vm1_nic1 : %s, vm1_nic2: %s, vm2_nic1 :%s, ipv4 :%s." %(vm1_nic1, vm1_nic2, vm2_nic1,ipv4)

    test_util.test_dsc("Create security groups.")
    sg1 = test_stub.create_sg(ipVersion = 6)
    sg2 = test_stub.create_sg(ipVersion = 6)
    sg3 = test_stub.create_sg(ipVersion = 6)
    sg_vm = test_sg_vm_header.ZstackTestSgVm()

    nic_uuid = vm2.get_vm().vmNics[0].uuid
    
    vm_nics = (nic_uuid, vm2)
    
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vm2_nic1, ipVersion = 6)
    rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vm2_nic1, ipVersion = 6)
    rule3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.INGRESS, vm2_nic1, ipVersion = 6)
    rule4 = test_lib.lib_gen_sg_rule(Port.rule4_ports, inventory.TCP, inventory.INGRESS, vm2_nic1, ipVersion = 6)
    rule5 = test_lib.lib_gen_sg_rule(Port.rule5_ports, inventory.TCP, inventory.INGRESS, vm2_nic1, ipVersion = 6)
    
    
    sg1.add_rule([rule1])
    sg2.add_rule([rule1, rule2, rule3])
    sg3.add_rule([rule3, rule4, rule5])


    test_util.test_dsc("Add nic to security group 1.")
    test_util.test_dsc("Allowed ports: %s" % Port.get_ports(Port.rule1_ports))
    sg_vm.attach(sg1, [vm_nics])

    test_util.test_dsc("Remove nic from security group 1.")
    test_util.test_dsc("Allowed ports: %s" % test_stub.target_ports)
    sg_vm.detach(sg1, nic_uuid)
  
    test_util.test_dsc("Remove rule1 from security group 1.")
    sg1.delete_rule([rule1])

    test_util.test_dsc("Add rule1, rule2, rule3 to security group 1.")
    test_util.test_dsc("Allowed ports: %s" % test_stub.target_ports)
    sg1.add_rule([rule1, rule2, rule3])

    test_util.test_dsc("Add nic to security group 1 again.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports
    test_util.test_dsc("Allowed ports: %s" % tmp_allowed_ports)
    sg_vm.attach(sg1, [vm_nics])
 
    test_util.test_dsc("Remove rule2/3 from security group 1.")
    test_util.test_dsc("Allowed ports: %s" % test_stub.rule1_ports)
    sg1.delete_rule([rule2, rule3])

    test_util.test_dsc("Add rule2, rule3 back to security group 1.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports
    test_util.test_dsc("Allowed ports: %s" % tmp_allowed_ports)
    sg1.add_rule([rule2, rule3])

    test_util.test_dsc("Remove rule2/3 from security group 1.")
    test_util.test_dsc("Allowed ports: %s" % test_stub.rule1_ports)
    sg1.delete_rule([rule2, rule3])
    #add sg2
    test_util.test_dsc("Add nic to security group 2.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports
    test_util.test_dsc("Allowed ports: %s" % tmp_allowed_ports)
    sg_vm.attach(sg2, [vm_nics])
    #add sg3
    test_util.test_dsc("Add nic to security group 3.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule2_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports
    test_util.test_dsc("Allowed ports (rule1+rule2+rul3+rule4+rule5): %s" % tmp_allowed_ports)
    sg_vm.attach(sg3, [vm_nics])
    #detach nic from sg2
    test_util.test_dsc("Remove security group 2 for nic.")
    tmp_allowed_ports = test_stub.rule1_ports + test_stub.rule3_ports + test_stub.rule4_ports + test_stub.rule5_ports
    test_util.test_dsc("Allowed ports (rule1+rule3+rule4+rule5): %s" % tmp_allowed_ports)
    sg_vm.detach(sg2, nic_uuid)
    #delete sg3
    test_util.test_dsc("Delete security group 3.")
    test_util.test_dsc("Allowed ports (rule1): %s" % test_stub.rule1_ports)
    sg_vm.delete_sg(sg3)
    test_obj_dict.rm_sg(sg3.security_group.uuid)
    #Cleanup
    sg_vm.delete_sg(sg2)
    test_obj_dict.rm_sg(sg2.security_group.uuid)
    sg_vm.delete_sg(sg1)
    test_obj_dict.rm_sg(sg1.security_group.uuid)
    vm1.destroy()
    vm2.destroy()
    test_util.test_pass('Security Group Vlan VirtualRouter VMs Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
