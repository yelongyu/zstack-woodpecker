'''
Test change cpu and memory configuration when VM is running
@author: quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
#import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Test update instance offering')

    vm = test_stub.create_basic_vm()
    instance_offering = test_lib.lib_get_instance_offering_by_uuid(vm.get_vm().instanceOfferingUuid)
    test_obj_dict.add_vm(vm)
    vm_ops.update_vm(vm.get_vm().uuid, instance_offering.cpuNum * 2, None)
    vm_ops.update_vm(vm.get_vm().uuid, None, instance_offering.memorySize * 2)

    vm.update()
    if (vm.get_vm().cpuNum != instance_offering.cpuNum):
        test_util.test_fail("cpuNum change is not expected to take effect before Vm restart")
    if (vm.get_vm().memorySize != instance_offering.memorySize):
        test_util.test_fail("memorySize change is not expected to take effect before Vm restart")

    vm.stop()
    vm.update()
    if (vm.get_vm().cpuNum != instance_offering.cpuNum):
        test_util.test_fail("cpuNum change is not expected to take effect before Vm restart")
    if (vm.get_vm().memorySize != instance_offering.memorySize):
        test_util.test_fail("memorySize change is not expected to take effect before Vm restart")

    vm.start()
    if (vm.get_vm().cpuNum != instance_offering.cpuNum * 2):
        test_util.test_fail("cpuNum change is expected to take effect after Vm restart")
    if (vm.get_vm().memorySize != instance_offering.memorySize * 2):
        test_util.test_fail("memorySize change is expected to take effect after Vm restart")

    vm.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Test update instance cpu memory Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
