'''

Test DetachSecurityGroupFromL3 API. This case might impact other test case,
if they are testing security group on the same L3 network. So this case should
not be executed parallelly with other test cases. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
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
    vm1.check()
    vm2.check()
    vm3.check()

    test_util.test_dsc("Create security groups.")
    sg1 = test_stub.create_sg()
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg_vm = test_sg_vm_header.ZstackTestSgVm()
    sg_vm.check()

    l3_uuid = vm1.vm.vmNics[0].l3NetworkUuid

    vr_vm = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vm3_ip = test_lib.lib_get_vm_nic_by_l3(vm3.vm, l3_uuid).ip
    
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vm3_ip)
    rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vm3_ip)
    rule3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.INGRESS, vm3_ip)

    sg1.add_rule([rule1])
    sg_vm.add_stub_vm(l3_uuid, vm3)
    sg_vm.check()

    nic_uuid1 = vm1.vm.vmNics[0].uuid
    nic_uuid2 = vm2.vm.vmNics[0].uuid
    vm1_nics = (nic_uuid1, vm1)
    vm2_nics = (nic_uuid2, vm2)
    
    #test_stub.lib_add_sg_rules(sg1.uuid, [rule0, rule1])
    
    test_util.test_dsc("Add vm 1 nic to security group 1.")
    test_util.test_dsc("Allowed ingress ports: %s" % test_stub.rule1_ports)
    sg_vm.attach(sg1, [vm1_nics])
    sg_vm.check()

    test_util.test_dsc("Detach security group 1 from vm1's l3 network.")
    test_util.test_dsc("VM1 nic will be automatically removed from SG1")
    sg_vm.detach_l3(sg1, l3_uuid)
    sg_vm.check()
    
    test_util.test_dsc("Add vm 1 & vm 2 nics to security group 1.")
    sg_vm.attach(sg1, [vm1_nics, vm2_nics])
    sg_vm.check()

    test_util.test_dsc("Detach security group 1 from vm1's l3 network. It will cause both vm1 and vm2 nics are detached from sg1.")
    sg_vm.detach_l3(sg1, l3_uuid)
    sg_vm.check()

    #Reboot Vm1 and check sg again.
    vm1.reboot()
    vm1.check()
    sg_vm.check()

    test_util.test_dsc("Add vm 1 & vm 2 nics to security group 1.")
    sg_vm.attach(sg1, [vm1_nics, vm2_nics])
    sg_vm.check()

    test_util.test_dsc("Remove rule1 from security group 1.")
    sg1.delete_rule([rule1])
    sg_vm.check()
    
    test_util.test_dsc("Add rule1, rule2, rule3 to security group 1.")
    test_util.test_dsc("Allowed ingress ports: %s" % test_stub.target_ports)
    sg1.add_rule([rule1, rule2, rule3])
    sg_vm.check()

    test_util.test_dsc("Detach security group 1 from vm1's l3 network. It will cause both vm1 and vm2 nics are detached from sg1.")
    sg_vm.detach_l3(sg1, l3_uuid)
    sg_vm.check()

    #delete sg1
    test_util.test_dsc("Delete security group 1.")
    sg_vm.delete_sg(sg1)
    test_obj_dict.rm_sg(sg1.security_group.uuid)
    sg_vm.check()

    #Cleanup
    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    vm3.destroy()
    test_obj_dict.rm_vm(vm3)
    test_util.test_pass('Security Group Detach from L3 network with 2 VMs on virtual router Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
