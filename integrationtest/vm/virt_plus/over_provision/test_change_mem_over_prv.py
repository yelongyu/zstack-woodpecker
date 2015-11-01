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
original_rate = None

def test():
    global original_rate
    test_util.test_dsc('Change Test memory over provision method')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    host = host[0]
    over_provision_rate1 = 2
    over_provision_rate2 = 1.5

    host_res = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid])
    avail_mem = host_res.availableMemory
    if avail_mem <= 1024*1024*1024:
        test_util.test_skip('Available memory is less than 512MB, skip test.')
        return True

    original_rate = test_lib.lib_set_provision_memory_rate(over_provision_rate1)

    vm = test_stub.create_vm(vm_name = 'mem_over_prs_vm_1')
    test_obj_dict.add_vm(vm)

    test_lib.lib_set_provision_memory_rate(over_provision_rate2)
    vm.destroy()

    vm = test_stub.create_vm(vm_name = 'mem_over_prs_vm_2')
    test_obj_dict.add_vm(vm)

    test_lib.lib_set_provision_memory_rate(original_rate)
    vm.destroy()

    host_res2 = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid])
    avail_mem2 = host_res2.availableMemory
    if avail_mem2 != avail_mem:
        test_util.test_fail('Available memory: %d is different with original available memory: %d' % (avail_mem2, avail_mem))
    else:
        test_util.test_logger('Available memory: %d is same with original available memory.' % avail_mem2)
    
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Change Memory Over Provision Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if original_rate:
        test_lib.lib_set_provision_memory_rate(original_rate)
