'''
@author: GuoCan
'''
import os
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

Port = test_state.Port
ct_original = None

def test():
    global test_obj_dict
    global Port
    global ct_original

    # close ip_spoofing; keep the original value, used to restore the original state
    if con_ops.get_global_config_value('vm', 'cleanTraffic') == 'false' :
        ct_original ='false'       
    else:
        ct_original ='true'
		con_ops.change_global_config('vm', 'cleanTraffic', 'false') 
        
        
    # create 3 vlan_vm: vm change ip, vm2 ping vm and create vm3 to use its ip
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
    l3_uuid = vm_inv.vmNics[0].l3NetworkUuid
    
    vm2 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm2)
    vm2.check()
    vm2_ip = vm2.get_vm().vmNics[0].ip
    
    # create vm3; vm,vm2,vm3 are in the same network segment
    vm3 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm3)
    vm3.check()
    # vm's new ip is set to vm3's ip
    new_vm_ip = vm3.get_vm().vmNics[0].ip
    vm3.destroy()
    test_obj_dict.rm_vm(vm3)    
    

    # create security group and add rule
    sg_vm = test_sg_vm_header.ZstackTestSgVm()
    sg = test_sg_header.ZstackTestSecurityGroup()
    sg_creation_option = test_util.SecurityGroupOption()
    sg_creation_option.set_name('test_sg')
    sg_creation_option.set_description('test sg description')
    sg.set_creation_option(sg_creation_option)
    sg.create()
    test_obj_dict.add_sg(sg.security_group.uuid)
    
    # create SG rule1: allow icmp to vm2
    rule1 = test_lib.lib_gen_sg_rule(Port.icmp_ports, inventory.ICMP, inventory.EGRESS, vm2_ip)
    # create SG rule2: allow icmp from vm2
    rule2 = test_lib.lib_gen_sg_rule(Port.icmp_ports, inventory.ICMP, inventory.INGRESS, vm2_ip)
    sg.add_rule([rule1, rule2])
    
    sg_vm.add_stub_vm(l3_uuid, vm2)
    sg_vm.check()
    
    # vm binding security group
    sg_vm.attach(sg, [(vm.get_vm().vmNics[0].uuid, vm)])
    sg_vm.check()
    
    
    # change vm_ip
    cmd = 'ifconfig eth0 %s' %new_vm_ip
    try:
        rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd, 90)
    except:
        pass
        
    
    # vm2 ping vm
    test_lib.lib_check_ping(vm2.get_vm(), new_vm_ip)
		
        
    sg_vm.delete_sg(sg)
    sg_vm.check()
    test_obj_dict.rm_sg(sg.security_group.uuid)
    vm.destroy()
    vm2.destroy()
    sg_vm.check()
    test_obj_dict.rm_vm(vm)
    test_obj_dict.rm_vm(vm2)
    con_ops.change_global_config('vm', 'cleanTraffic', ct_original)
    test_util.test_pass('Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    global Port
    global ct_original
    con_ops.change_global_config('vm', 'cleanTraffic', ct_original) 
    test_lib.lib_error_cleanup(test_obj_dict)
