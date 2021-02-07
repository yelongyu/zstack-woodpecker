'''

New Integration Test for creating KVM VM.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import os
# import arm.test_stub as test_stub

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_stub,test_obj_dict
    vm = test_stub.create_arm_vm()
    test_obj_dict.add_vm(vm)

    vm.check()
    vm.suspend()
    vm.check()
    vm.resume()
    vm.check()
    vm.reboot()
    vm.check()
    l3_name=os.environ.get('l3PublicNetworkName')
    l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm.add_nic(l3_uuid)
    # vm.check()
    cpuNum = 2
    memorySize = 666 * 1024 * 1024
    new_offering = test_lib.lib_create_instance_offering(cpuNum = cpuNum,\
            memorySize = memorySize)
    test_obj_dict.add_instance_offering(new_offering)

    vm.stop()
    vm.change_instance_offering(new_offering.uuid)
    vm.check()
    vm.start()
    vm.stop()
    vm.check()
    vm.reinit()
    vm.check()
    #time.sleep(5)
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
