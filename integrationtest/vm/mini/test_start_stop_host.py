'''
This case can not execute parallelly
@author: Youyk
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    test_util.test_dsc('Test Host Start/Stop function')
    vm = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm)

    zone_uuid = vm.get_vm().zoneUuid
    host = test_lib.lib_get_vm_host(vm.get_vm())
    host_uuid = host.uuid

    tot_res1 = test_lib.lib_get_cpu_memory_capacity([zone_uuid])
    
    host_ops.change_host_state(host_uuid, "Disabled" )
    time.sleep(5)


    host_ops.change_host_state(host_uuid, "Enabled" )


    vm = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm)

    tot_res4 = test_lib.lib_get_cpu_memory_capacity([zone_uuid])

    vm.destroy()

    test_util.test_pass('Reconnect Host and Test CPU/Memory Capacity Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
