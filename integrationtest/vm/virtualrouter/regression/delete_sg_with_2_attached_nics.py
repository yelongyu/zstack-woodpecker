'''

Test deleting SG with 2 attached NICs.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
Port = test_state.Port

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
    vm1.check()
    vm2.check()

    test_util.test_dsc("Create security groups.")
    sg1 = test_stub.create_sg()
    sg_vm = test_sg_vm_header.ZstackTestSgVm()
    test_obj_dict.set_sg_vm(sg_vm)

    l3_uuid = vm1.vm.vmNics[0].l3NetworkUuid

    vr_vm = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vm2_ip = test_lib.lib_get_vm_nic_by_l3(vm2.vm, l3_uuid).ip
    
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vm2_ip)
    rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vm2_ip)
    rule3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.INGRESS, vm2_ip)

    sg1.add_rule([rule1])
    sg1.add_rule([rule2])
    sg1.add_rule([rule3])
    sg_vm.check()

    nic_uuid1 = vm1.vm.vmNics[0].uuid
    nic_uuid2 = vm2.vm.vmNics[0].uuid
#    nic_uuid3 = vm2.vm.vmNics[0].uuid
    vm1_nics = (nic_uuid1, vm1)
    vm2_nics = (nic_uuid2, vm2)
#    vm3_nics = (nic_uuid3, vm3)
    
    #test_stub.lib_add_sg_rules(sg1.uuid, [rule0, rule1])
    
    test_util.test_dsc("Add nic to security group 1.")
    test_util.test_dsc("Allowed ingress ports: %s" % test_stub.rule1_ports)
    #sg_vm.attach(sg1, [vm1_nics, vm2_nics, vm3_nics])
    sg_vm.attach(sg1, [vm1_nics, vm2_nics])
    sg_vm.check()

    sg_vm.delete_sg(sg1)
    sg_vm.check()
    
    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    test_util.test_pass('Delete Security Group with 2 attached NICs Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
