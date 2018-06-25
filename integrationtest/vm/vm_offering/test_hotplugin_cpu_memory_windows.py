'''
@author: FangSun
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import time
import random

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    test_util.test_dsc("STEP1: Ceate vm instance offering")
    vm_instanc_offering = test_lib.lib_create_instance_offering(cpuNum = 2,
                                                                memorySize = 2 * 1024 * 1024 * 1024)
    test_obj_dict.add_instance_offering(vm_instanc_offering)

    test_util.test_dsc("STEP2: Ceate vm and wait until it up for testing")
    vm = test_stub.create_vm(vm_name = 'window-telnet', image_name = "imageName_windows",
                             instance_offering_uuid=vm_instanc_offering.uuid)
    test_obj_dict.add_vm(vm)
    time.sleep(10)

    test_util.test_dsc("STEP3: Hot Plugin CPU and Memory and check capacity")
    cpu_change = random.randint(1,5)
    mem_change = random.randint(1,500) * 1024 * 1024

    with test_stub.CapacityCheckerContext(vm, cpu_change, mem_change, window=True):
        # wait for 90s to ensure all the windows services up
        time.sleep(90)
        vm_ops.update_vm(vm.get_vm().uuid, vm_instanc_offering.cpuNum+cpu_change,
                         vm_instanc_offering.memorySize+mem_change)
        vm.update()
        time.sleep(10)

    test_util.test_dsc("STEP4: Destroy test object")
    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('VM online change instance offering Test Pass')


def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
