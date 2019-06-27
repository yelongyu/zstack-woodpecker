'''

New Integration Test for instance offering allocator strategy 'DesignatedHostAllocatorStrategy'.

@author: chenyuan.xu
'''
import zstackwoodpecker.test_util as test_util
import os
import time
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global vm

    test_util.test_dsc('create instance offering')
    instance_offering_option = test_util.InstanceOfferingOption()
    instance_offering_option.set_cpuNum(1)
    instance_offering_option.set_memorySize(1*1024*1024*1024)
    instance_offering_option.set_allocatorStrategy("")
    instance_offering_option.set_type("UserVm")
    instance_offering_option.set_name('new_offering')
    instance_offering_option.set_allocatorStrategy("DesignatedHostAllocatorStrategy")
    new_offering = vm_ops.create_instance_offering(instance_offering_option)
    test_obj_dict.add_instance_offering(new_offering)    
    image_name = os.environ.get('imageName_s')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm = test_stub.create_vm_with_instance_offering('test-vm',image_name,l3_name, new_offering)
    test_obj_dict.add_vm(vm)
#    vm.check()
    for i in (0, 15):
        host_ip1 = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
        vm.stop()
        vm.start() 
        host_ip2 = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
        if host_ip1 == host_ip2:
            test_util.test_fail("Current host ip is the same as the last host ip in %s round." % i)

    vm.destroy()
    test_util.test_pass('Instance Offering Designated Host Allocator Strategy Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
