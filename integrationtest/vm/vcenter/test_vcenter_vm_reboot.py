'''
test for vm reboot in newly add vcenter
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import test_stub
import os



vm = None

def test():
    global vm

    ova_image_name = os.environ['vcenterDefaultmplate']
    network_pattern1 = os.environ['vcenterDefaultNetwork']


    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm-delete-test', image_name = ova_image_name, l3_name = network_pattern1)

    vm.check()

    vm.reboot()
    vm.check()

    vm.destroy()
    vm.check()
    vm.expunge()

    test_util.test_pass("vm reboot of vcenter test passed.")



def error_cleanup():
    global vm
    if vm:
        vm.destroy()
        vm.expunge()
