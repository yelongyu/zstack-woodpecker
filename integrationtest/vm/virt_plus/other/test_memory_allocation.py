'''
This case can not execute parallelly.

This case will try to over create VMs in one host, then delete all successful
created VM. Finally it will compare the host available memory before creating
vm and after destroying vm. 
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
original_rate = None
new_offering_uuid = None

def test():
    global original_rate
    global new_offering_uuid
    test_util.test_dsc('Test memory allocation and reclaiming.')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    host = host[0]
    over_provision_rate = 1
    target_vm_num = 5

    host_res = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid])
    #avail_mem = host_res.availableMemory * over_provision_rate
    avail_mem = host_res.availableMemory
    if avail_mem <= 1024*1024*1024:
        test_util.test_skip('Available memory is less than 1024MB, skip test.')
        return True

    original_rate = test_lib.lib_set_provision_memory_rate(over_provision_rate)
    host_res = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid])
    avail_mem = host_res.availableMemory

    test_mem = avail_mem / target_vm_num
    new_offering_mem = test_mem
    new_offering = test_lib.lib_create_instance_offering(memorySize = new_offering_mem)

    new_offering_uuid = new_offering.uuid

    rounds = 0
    while (rounds < 3):
        times = 1
        while (times <= (target_vm_num)):
            try:
                vm = test_stub.create_vm(vm_name = 'mem_reclaim_vm_%d' % times, \
                        host_uuid = host.uuid, \
                        instance_offering_uuid = new_offering.uuid)
                test_obj_dict.add_vm(vm)
            except Exception as e:
                test_util.test_logger("VM Creation Failure in memory reclaiming test. :%s " % e)
                pass

            times += 1

        for vm in test_obj_dict.get_all_vm_list():
            try:
                vm.destroy()
                test_obj_dict.rm_vm(vm)
            except Exception as e:
                test_util.test_logger("VM Destroying Failure in memory reclaiming test. :%s " % e)
                pass

        host_res2 = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid])
        avail_mem2 = host_res2.availableMemory
        if avail_mem2 != avail_mem:
            test_util.test_fail('Available memory reclaiming is not correct. Current available memory : %d, original available memory: %d , after creating and destroying %d vms. in round: %d' % (avail_mem2, avail_mem, target_vm_num, rounds))

        rounds += 1
    
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
