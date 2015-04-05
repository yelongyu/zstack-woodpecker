'''

New Integration Test for testing security group.

@author: ZX
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import test_stub
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import apibinding.inventory as inventory

Port = test_state.Port
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    vm = test_stub.create_vm()
    test_obj_dict.add_vm(vm)
    vm.check()
    # This is very basic and raw SG testing. The formal test should use the functions in test_lib.
    sg_vm = test_sg_vm_header.ZstackTestSgVm()
    sg = test_sg_header.ZstackTestSecurityGroup()
    sg_creation_option = test_util.SecurityGroupOption()
    sg_creation_option.set_name('test_sg')
    sg_creation_option.set_description('test sg description')
    sg.set_creation_option(sg_creation_option)
    sg.create()
    test_obj_dict.add_sg(sg.security_group.uuid)

    rule = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, '10.0.101.10')
    
    sg.add_rule([rule])

    sg_vm.attach(sg, [(vm.vm.vmNics[0].uuid, vm)])

    sg_vm.check()

    sg_vm.detach(sg, vm.vm.vmNics[0].uuid)

    sg_vm.attach(sg, [(vm.vm.vmNics[0].uuid, vm)])

    sg_vm.check()

    sg_vm.delete_sg(sg)
    sg_vm.check()
    test_obj_dict.rm_sg(sg.security_group.uuid)
    vm.destroy()
    sg_vm.check()

    test_util.test_pass('Create VM with simple Security Group Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
