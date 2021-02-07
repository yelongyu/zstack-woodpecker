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

def compare_capacity(res1, res2, cpu_free = 0, memory_free = 0):
    if res1.availableCpu != res2.availableCpu - cpu_free:
        test_util.test_logger('available CPU are different. res1: %s, res2: %s\
                ' % (res1.availableCpu, res2.availableCpu))
        return False

    if res1.totalCpu != res2.totalCpu:
        test_util.test_logger('total CPU are different. res1: %s, res2: %s\
                ' % (res1.totalCpu, res2.totalCpu))
        return False

    if res1.availableMemory != res2.availableMemory - memory_free:
        test_util.test_logger('available Memory are different. res1: %s, res2: %s\
                ' % (res1.availableMemory, res2.availableMemory))
        return False

    if res1.totalMemory != res2.totalMemory:
        test_util.test_logger('available Memory are different. res1: %s, res2: %s\
                ' % (res1.totalMemory, res2.totalMemory))
        return False

    return True

def test():
    test_util.test_dsc('Test Host Reconnect function and check if the available CPU and memory number are aligned between before and after reconnect action')
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm)

    zone_uuid = vm.get_vm().zoneUuid
    host = test_lib.lib_get_vm_host(vm.get_vm())
    host_uuid = host.uuid

    tot_res1 = test_lib.lib_get_cpu_memory_capacity([zone_uuid])
    
    host_ops.reconnect_host(host_uuid)
    time.sleep(5)

    tot_res2 = test_lib.lib_get_cpu_memory_capacity([zone_uuid])

    if compare_capacity( tot_res1, tot_res2):
        test_util.test_logger("the resource consumption are same after reconnect host")
    else:
        test_util.test_fail("the resource consumption are different after reconnect host: %s " % host_uuid)

    vm_offering_uuid = vm.get_vm().instanceOfferingUuid
    cond = res_ops.gen_query_conditions('uuid', '=', vm_offering_uuid)
    vm_offering = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)[0]
    vm_cpu = vm_offering.cpuNum
    vm_memory = vm_offering.memorySize
    
    vm.destroy()
    test_obj_dict.rm_vm(vm)

    tot_res3 = test_lib.lib_get_cpu_memory_capacity([zone_uuid])
    if compare_capacity(tot_res1, tot_res3, vm_cpu, vm_memory):
        test_util.test_logger("the resource consumption are aligned after destroy a vm")
    else:
        test_util.test_fail("the resource consumption are not aligned after destroy vm: %s on host: %s" % (vm.get_vm().uuid, host_uuid))

    test_stub.ensure_hosts_connected(120)
    test_stub.ensure_pss_connected()    
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm)

    tot_res4 = test_lib.lib_get_cpu_memory_capacity([zone_uuid])

    if compare_capacity(tot_res1, tot_res4):
        test_util.test_logger("the resource consumption are aligned after create a new vm")
    else:
        test_util.test_fail("the resource consumption are not aligned after create a new vm: %s " % vm.get_vm().uuid)

    vm.destroy()

    test_util.test_pass('Reconnect Host and Test CPU/Memory Capacity Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
