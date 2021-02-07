'''

Test shared Security Group for 2 VMs with ingress connection

@author: Pengtao.Zhang
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory
import zstacklib.utils.ssh as ssh
import time
import os

global ipv6
ipv6 = "ipv6"
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
    image_name = os.environ.get('ipv6ImageName')
    ipv4_net_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3PublicNetworkName')).uuid
    ipv6_net_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3PublicNetworkName1')).uuid
    print "ipv4_net_uuid is : %s , ipv6_net_uuid is : %s" %(ipv4_net_uuid, ipv6_net_uuid)

    vm1 = test_stub.create_vm(l3_name = os.environ.get('l3PublicNetworkName'), vm_name = 'vm_1 IPv6 2 stack test', system_tags = ["dualStackNic::%s::%s" %(ipv4_net_uuid, ipv6_net_uuid)], image_name = image_name)
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_vm(l3_name = os.environ.get('l3PublicNetworkName'), vm_name = 'vm_2 IPv6 2 stack test', system_tags = ["dualStackNic::%s::%s" %(ipv4_net_uuid, ipv6_net_uuid)], image_name = image_name)
    test_obj_dict.add_vm(vm2)
    time.sleep(120) #waiting for vm bootup
    vm1_ip1 = vm1.get_vm().vmNics[0].usedIps[0].ip
    vm1_ip2 = vm1.get_vm().vmNics[0].usedIps[1].ip
    vm2_ip1 = vm2.get_vm().vmNics[0].usedIps[0].ip
    vm2_ip2 = vm2.get_vm().vmNics[0].usedIps[1].ip
    if r"172." in vm1_ip1:
        vm1_ipv4 = vm1_ip1
        vm1_ipv6 = vm1_ip2
    else:
        vm1_ipv4 = vm1_ip2
        vm1_ipv6 = vm1_ip1

    if r"172." in vm2_ip1:
        vm2_ipv4 = vm2_ip1
        vm2_ipv6 = vm2_ip2
    else:
        vm2_ipv4 = vm2_ip2
        vm2_ipv6 = vm2_ip1

    print "vm1_ipv6 : %s, vm1_ipv4: %s, vm2_ipv6 :%s,vm2_ipv4 :%s, ipv4 :%s, ipv6 :%s." %(vm1_ipv6, vm1_ipv4, vm2_ipv6, vm2_ipv4, vm2_ipv4, vm2_ipv6)
    cmd = "ping6 -c 4 %s" %(vm2_ipv6)
    (retcode, output, erroutput) = ssh.execute(cmd, vm1_ipv4, "root", "password", True, 22)
    cmd1 = "ping -c 4 %s" %(vm2_ipv4)
    (retcode1, output1, erroutput1) = ssh.execute(cmd1, vm1_ipv4, "root", "password", True, 22)
    print "retcode is: %s; output is : %s.; erroutput is: %s" %(retcode, output , erroutput)
    print "retcode1 is: %s; output1 is : %s.; erroutput1 is: %s" %(retcode1, output1 , erroutput1)

    test_util.test_dsc("Create security groups.")
    sg1 = test_stub.create_sg(ipVersion = 6,sg_name = 'sg1')
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg2 = test_stub.create_sg(ipVersion = 6, sg_name = 'sg2')
    test_obj_dict.add_sg(sg2.security_group.uuid)
    sg_vm = test_sg_vm_header.ZstackTestSgVm()

    l3_uuid = ipv6_net_uuid
    vm1_nic_uuid = vm1.get_vm().vmNics[0].uuid
    vm2_nic_uuid = vm2.get_vm().vmNics[0].uuid
    print "vm1_nic_uuid :%s, vm2_nic_uuid :%s ."%(vm1_nic_uuid, vm2_nic_uuid)

    #Attach security group to l3 network
    net_ops.attach_security_group_to_l3(sg1.security_group.uuid, l3_uuid)
    net_ops.attach_security_group_to_l3(sg2.security_group.uuid, l3_uuid)

    #Add vm1 nic to security group
    sg_vm.attach(sg1, [(vm1_nic_uuid, vm1)], ipv6 = "ipv6")
    sg_vm.attach(sg2, [(vm2_nic_uuid, vm2)], ipv6 = "ipv6")

    rule1_1 = test_lib.lib_gen_sg_rule(Port.icmp_ports, inventory.ICMP, inventory.INGRESS, vm2_ipv6, ipVersion = 6)
    rule1_2 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vm2_ipv6, ipVersion = 6)
    rule1_3 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.UDP, inventory.INGRESS, vm2_ipv6, ipVersion = 6)

    sg1.add_rule([rule1_1,rule1_2,rule1_3], [sg2.security_group.uuid])
    sg_vm.add_stub_vm(l3_uuid, vm2)
    sg_vm.delete_stub_vm(l3_uuid)

    rule2_1 = test_lib.lib_gen_sg_rule(Port.icmp_ports, inventory.ICMP, inventory.INGRESS, vm1_ipv6, ipVersion = 6)
    rule2_2 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vm1_ipv6, ipVersion = 6)
    rule2_3 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.UDP, inventory.INGRESS, vm1_ipv6, ipVersion = 6)

    sg2.add_rule([rule2_1,rule2_2,rule2_3], [sg1.security_group.uuid])
    sg_vm.add_stub_vm(l3_uuid, vm1)

    try:
        test_lib.lib_open_vm_listen_ports(vm1.vm, Port.ports_range_dict['rule1_ports'], l3_uuid, target_ip = vm1_ipv4, target_ipv6 = vm1_ipv6)
        test_lib.lib_open_vm_listen_ports(vm2.vm, Port.ports_range_dict['rule1_ports'], l3_uuid, target_ip = vm2_ipv4, target_ipv6 = vm2_ipv6)
        test_lib.lib_check_vm_ports_in_a_command(vm1.vm, vm2.vm, Port.ports_range_dict['rule1_ports'], [], target_ipv6 = vm2_ipv6)
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
