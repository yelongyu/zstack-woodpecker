'''
@author: Youyk
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Test VM change instance offering')

    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)

    cpuNum = 2
    cpuSpeed = 222
    memorySize = 666 * 1024 * 1024
    new_offering = test_lib.lib_create_instance_offering(cpuNum = cpuNum,\
            cpuSpeed = cpuSpeed, memorySize = memorySize)

    test_obj_dict.add_instance_offering(new_offering)
    new_offering_uuid = new_offering.uuid

    vm.stop()
    vm.change_instance_offering(new_offering_uuid)
    vm.start()
    vm.check()
    vm.reboot()
    vm.check()
    cpuNum = 1
    cpuSpeed = 111
    memorySize = 555 * 1024 * 1024
    new_offering = test_lib.lib_create_instance_offering(cpuNum = cpuNum,\
            cpuSpeed = cpuSpeed, memorySize = memorySize)

    test_obj_dict.add_instance_offering(new_offering)
    new_offering_uuid = new_offering.uuid
    vm.stop()
    vm.change_instance_offering(new_offering_uuid)
    vm.start()
    vm.check()

    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('VM change instance offering Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
