'''

For Stress Testing: create 1 VM with VR and SG rule, then destroy it after 3s. 
The test will create 2 SG for VM with 200 rules each. 

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
sg_num = 2
rule_num = 200

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
    
    rule_list = []
    for j in range(rule_num):
        target_ip = '%s%s' % (target_ip_prefix, str(1+j))
        rule = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, target_ip)
        rule_list.append(rule)

    sg1 = test_stub.create_sg()
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg1.add_rule(rule_list)
    sg_vm.attach(sg1, [vm_nics])

    rule_list = []
    for j in range(rule_num):
        target_ip = '%s%s' % (target_ip_prefix, str(1+j))
        rule = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.EGRESS, target_ip)
        rule_list.append(rule)

    sg2 = test_stub.create_sg()
    test_obj_dict.add_sg(sg2.security_group.uuid)
    sg2.add_rule(rule_list)
    sg_vm.attach(sg2, [vm_nics])

    sg1_rules = test_lib.lib_get_sg_rule(sg1.security_group.uuid)
    if len(sg1_rules) != 200:
        test_util.test_fail("Did not find 200 SG rules for SG1: %s. We only catch %s rules" % (sg1.security_group.uuid, len(sg1_rules)))

    sg2_rules = test_lib.lib_get_sg_rule(sg2.security_group.uuid)
    if len(sg2_rules) != 200:
        test_util.test_fail("Did not find 200 SG rules for SG2: %s. We only catch %s rules" % (sg2.security_group.uuid, len(sg2_rules)))

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
