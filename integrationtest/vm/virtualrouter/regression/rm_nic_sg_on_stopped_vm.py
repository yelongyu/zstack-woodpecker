'''

The test will test if remove stopped VM NIC from SG could be success.

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
    sg_vm = test_sg_vm_header.ZstackTestSgVm()
    
    nic_uuid = vm1.vm.vmNics[0].uuid
    vm_nics = (nic_uuid, vm1)
    l3_uuid = vm1.vm.vmNics[0].l3NetworkUuid
    vr_vm = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vm2_ip = test_lib.lib_get_vm_nic_by_l3(vm2.vm, l3_uuid).ip
    
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.EGRESS, vm2_ip)
    rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.EGRESS, vm2_ip)
    rule3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.EGRESS, vm2_ip)

    sg1.add_rule([rule1, rule2, rule3])

    sg_vm.add_stub_vm(l3_uuid, vm2)


    #add sg1
    test_util.test_dsc("Add VM1 nic to security group 1.")
    sg_vm.attach(sg1, [vm_nics])
    sg_vm.check()
    
    #shutdown vm1
    test_util.test_dsc("Shutdown VM1")
    vm1.stop()

    #remove vm1 nic from sg1
    test_util.test_dsc("Remove nic from security group 1 to stopped vm1.")
    sg_vm.detach(sg1, nic_uuid)

    test_util.test_dsc("Start VM1")
    vm1.start()
    vm1.check()
    sg_vm.check()

    vm1.destroy()
    vm2.destroy()
    sg_vm.delete_sg(sg1)
    test_util.test_pass('Detach stopped VM NIC from Security Group Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
