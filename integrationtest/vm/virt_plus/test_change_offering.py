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
import zstackwoodpecker.operations.vm_operations as vm_ops

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global new_offering_uuid
    test_util.test_dsc('Test memory status after change VM offering')

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    host_uuid = host[0].uuid
    zone_uuid = host[0].zoneUuid
    host_avail_mem1 = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host_uuid]).availableMemory
    zone_avail_mem1 = test_lib.lib_get_cpu_memory_capacity(zone_uuids = [zone_uuid])
    #unit is KB
    new_offering1 = test_lib.lib_create_instance_offering(cpuNum = 1, \
            cpuSpeed = 16, memorySize = 536870912, name = 'new_instance1')

    test_obj_dict.add_instance_offering(new_offering1)
    new_offering_uuid = new_offering1.uuid

    vm = test_stub.create_vm(vm_name = 'test_avail_memory', \
            instance_offering_uuid = new_offering1.uuid)
    test_obj_dict.add_vm(vm)

    vm.stop()

    new_offering2 = test_lib.lib_create_instance_offering(cpuNum = 1, \
            cpuSpeed = 16, memorySize = 1073741824, name = 'new_instance2')

    test_obj_dict.add_instance_offering(new_offering2)
    new_offering_uuid = new_offering2.uuid
    vm_inv = vm.get_vm()
    vm.change_instance_offering(new_offering_uuid)
    vm.start()
    host_avail_mem2 = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host_uuid]).availableMemory
    zone_avail_mem2 = test_lib.lib_get_cpu_memory_capacity(zone_uuids = [zone_uuid])

    if host_avail_mem2 >= host_avail_mem1 :
        test_util.test_fail('Host available memory is not correct after change vm template. Previous value: %s , Current value: %s' % (host_avail_mem1, host_avail_mem2))

    if zone_avail_mem2 >= zone_avail_mem1 :
        test_util.test_fail('Zone available memory is not correct after change vm template. Previous value: %s , Current value: %s' % (zone_avail_mem1, zone_avail_mem2))

    if (zone_avail_mem1 - zone_avail_mem2) != (host_avail_mem1 - host_avail_mem2):
        test_util.test_fail('available memory change is not correct after change vm template. zone changed value: %s , host changed value: %s' % ((zone_avail_mem1 - zone_avail_mem2), (host_avail_mem1 - host_avail_mem2)))

    test_util.test_pass('Test available memory when changing instance offering Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
