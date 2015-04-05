'''

New Integration test for testing vms migration with SG rules

Test Steps:
    1. Create 3 VMs for SG testing.
    2. 2 VMs are assigned in same SG group with SG rules
    3. migrate 2 VMs to different Host
    4. Test SG after migration.

@author: Youyk
'''

import time
import os
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory

Port = test_state.Port
test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()

def test():
    vm1 = test_stub.create_vr_vm('migrate_vm1', 'imageName_s', 'l3VlanNetwork3')
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_vr_vm('migrate_vm2', 'imageName_s', 'l3VlanNetwork3')
    test_obj_dict.add_vm(vm2)
    vm3 = test_stub.create_vr_vm('migrate_vm3', 'imageName_s', 'l3VlanNetwork3')
    test_obj_dict.add_vm(vm3)
    vm1.check()
    vm2.check()
    vm3.check()

    test_util.test_dsc("Create security groups.")
    sg1 = test_stub.create_sg()
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg2 = test_stub.create_sg()
    test_obj_dict.add_sg(sg2.security_group.uuid)
    sg_vm = test_sg_vm_header.ZstackTestSgVm()
    sg_vm.check()

    l3_uuid = vm1.vm.vmNics[0].l3NetworkUuid

    vr_vm = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vm3_ip = test_lib.lib_get_vm_nic_by_l3(vm3.vm, l3_uuid).ip
    
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vm3_ip)
    rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vm3_ip)
    rule3 = test_lib.lib_gen_sg_rule(Port.rule3_ports, inventory.TCP, inventory.INGRESS, vm3_ip)

    sg1.add_rule([rule1])
    sg2.add_rule([rule1, rule2, rule3])
    sg_vm.add_stub_vm(l3_uuid, vm3)

    nic_uuid1 = vm1.vm.vmNics[0].uuid
    nic_uuid2 = vm2.vm.vmNics[0].uuid
    vm1_nics = (nic_uuid1, vm1)
    vm2_nics = (nic_uuid2, vm2)

    test_util.test_dsc("Add nic to security group 1.")
    test_util.test_dsc("Allowed ingress ports: %s" % test_stub.rule1_ports)
    sg_vm.attach(sg1, [vm1_nics, vm2_nics])
    sg_vm.attach(sg2, [vm1_nics, vm2_nics])
    
    test_stub.migrate_vm_to_random_host(vm1)
    test_stub.migrate_vm_to_random_host(vm2)
    test_stub.migrate_vm_to_random_host(vm3)
    vm1.check()
    vm2.check()
    vm3.check()
    sg_vm.check()

    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    vm3.destroy()
    test_obj_dict.rm_vm(vm3)
    sg_vm.delete_sg(sg1)
    test_obj_dict.rm_sg(sg1.security_group.uuid)
    sg_vm.delete_sg(sg2)
    test_obj_dict.rm_sg(sg2.security_group.uuid)
    test_util.test_pass('Migrate SG VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
