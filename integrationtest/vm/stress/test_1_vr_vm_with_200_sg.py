'''

For Stress Testing: create 1 VM with VR and SG rule, then destroy it after 3s. 
The test will totally create 200 different SG for 1 VM. Each SG has 5 different
rules. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import time
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

parallel_num = 10
sg_num = 200

def test():
    global test_obj_dict
    test_util.test_dsc("Create 1 VMs with vlan VR L3 network for SG testing.")
    vm1 = test_stub.create_sg_vm()
    test_obj_dict.add_vm(vm1)
    vm1.check()

    nic_uuid = vm1.vm.vmNics[0].uuid
    vm_nics = (nic_uuid, vm1)
    l3_uuid = vm1.vm.vmNics[0].l3NetworkUuid

    vr_vm = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vm1_ip = test_lib.lib_get_vm_nic_by_l3(vr_vm, l3_uuid).ip
    target_ip_prefix = '10.10.10.'
    
    test_util.test_dsc("Create security groups.")
    for i in range(sg_num):
        target_ip = '%s%s' % (target_ip_prefix, str(1+i))
        rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, target_ip)
        rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, target_ip)
        rule3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.INGRESS, target_ip)
        rule4 = test_lib.lib_gen_sg_rule(Port.rule4_ports, inventory.TCP, inventory.INGRESS, target_ip)
        rule5 = test_lib.lib_gen_sg_rule(Port.rule5_ports, inventory.TCP, inventory.INGRESS, target_ip)

        sg = test_stub.create_sg()
        test_obj_dict.add_sg(sg.security_group.uuid)
        sg.add_rule([rule1, rule2, rule3, rule4, rule5])
        sg_vm.attach(sg, [vm_nics])

    time.sleep(3)
    #need regularlly clean up log files in virtual router when doing stress test
    test_lib.lib_check_cleanup_vr_logs_by_vm(vm1.vm)
    #clean up all vm and sg
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create/Destroy VM with VR successfully')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
