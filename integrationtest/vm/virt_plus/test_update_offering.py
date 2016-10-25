'''
This case can not execute parallelly
@author: SyZhao
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
#import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
#import zstackwoodpecker.operations.vm_operations as vm_ops

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Test update instance offering')

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    host_uuid = host[0].uuid
    new_offering = test_lib.lib_create_instance_offering(cpuNum = 1, \
            cpuSpeed = 16, memorySize = 536870912, name = 'orgin_instance_name')

    test_obj_dict.add_instance_offering(new_offering)

    vm = test_stub.create_vm(vm_name = 'test_update_instance_offering', \
            host_uuid = host_uuid, \
            instance_offering_uuid = new_offering.uuid)
    test_obj_dict.add_vm(vm)

    vm.stop()

    #These parameters are need to be populated.
    updated_offering = test_lib.lib_update_instance_offering(new_offering.uuid, cpuNum = 2, cpuSpeed = 16, \
        memorySize = 1073741824, name = 'updated_instance_name', \
        volume_iops = None, volume_bandwidth = None, \
        net_outbound_bandwidth = None, net_inbound_bandwidth = None)

    vm.start()
    vm.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Test updated instance offering Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
