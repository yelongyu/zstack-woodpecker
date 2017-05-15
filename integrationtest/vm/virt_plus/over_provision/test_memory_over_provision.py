'''
This case can not execute parallelly
@author: Youyk
'''
import os
import zstacklib.utils.sizeunit as sizeunit
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
original_rate = None
new_offering_uuid = None

def test():
    global original_rate
    global new_offering_uuid
    test_util.test_dsc('Test memory over provision method')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    host = host[0]
    over_provision_rate = 2
    target_vm_num = 4

    host_res = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid])
    real_availableMemory = host_res.availableMemory
    avail_mem = real_availableMemory * over_provision_rate
    if avail_mem <= 1024*1024*1024:
        test_util.test_skip('Available memory is less than 512MB, skip test.')
        return True

    test_util.test_logger('host available memory is: %s' % host_res.availableMemory)

    original_rate = test_lib.lib_set_provision_memory_rate(over_provision_rate)

    new_offering_mem = int((avail_mem - 1) / target_vm_num)
    if (new_offering_mem % 2) != 0 :
        new_offering_mem = new_offering_mem - 1 
    new_offering = test_lib.lib_create_instance_offering(memorySize = new_offering_mem)

    new_offering_uuid = new_offering.uuid

    times = 1
    while (times <= target_vm_num):
        try:
            vm_name = 'mem_over_prs_vm_%d' % times
            vm = test_stub.create_vm(vm_name = vm_name, \
                    host_uuid = host.uuid, \
                    instance_offering_uuid = new_offering.uuid)
            test_obj_dict.add_vm(vm)
            host_res_new = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid])
            test_util.test_logger('After create vm: %s, host available memory is: %s' % (vm_name, host_res_new.availableMemory))
        except Exception as e:
            test_util.test_logger("Unexpected VM Creation Failure in memory over provision test. Previous available memory is %s" % host_res_new.availableMemory)
            raise e

        times += 1

    host_res2 = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid])
    avail_mem2 = host_res2.availableMemory
    if avail_mem2 > new_offering_mem:
        test_util.test_fail('Available memory: %d is still bigger than offering memory: %d , after creating 4 vms.' % (avail_mem2, new_offering_mem))
    
    try:
        vm = test_stub.create_vm(vm_name = 'mem_over_prs_vm_bad', \
                host_uuid = host.uuid, \
                instance_offering_uuid = new_offering.uuid)
        test_obj_dict.add_vm(vm)
    except:
        test_util.test_logger("Expected VM Creation Failure in memory over provision test. ")
    else:
        test_util.test_fail("The 5th VM is still created up, which is wrong")

    test_lib.lib_set_provision_memory_rate(original_rate)
    vm_ops.delete_instance_offering(new_offering_uuid)
    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('Memory Over Provision Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if original_rate:
        test_lib.lib_set_provision_memory_rate(original_rate)
    if new_offering_uuid:
        vm_ops.delete_instance_offering(new_offering_uuid)
