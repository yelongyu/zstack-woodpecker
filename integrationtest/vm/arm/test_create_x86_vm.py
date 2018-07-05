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
    vm = test_stub.create_x86_vm()
    test_obj_dict.add_vm(vm)
    vm.suspend()
    vm.resume()
    vm.reboot()

    l3_name=os.environ.get('l3VlanNetworkName2')
    l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm.add_nic(l3_uuid)

    cpuNum = 2
    memorySize = 666 * 1024 * 1024
    new_offering = test_lib.lib_create_instance_offering(cpuNum = cpuNum,\
            memorySize = memorySize)
    test_obj_dict.add_instance_offering(new_offering)

    vm.stop()
    vm.change_instance_offering(new_offering.uuid)
    vm.start()

    vm.stop()
    vm.reinit()
    #time.sleep(5)
    # vm.check()
    vm.clean()
    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
