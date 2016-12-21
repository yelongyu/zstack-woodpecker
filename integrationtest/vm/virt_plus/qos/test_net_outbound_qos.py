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
new_offering_uuid = None

def test():
    global new_offering_uuid
    test_util.test_dsc('Test VM network outbound bandwidth QoS by 1MB')

    #unit is KB
    net_bandwidth = 1024
    new_offering = test_lib.lib_create_instance_offering(net_outbound_bandwidth = net_bandwidth)

    new_offering_uuid = new_offering.uuid

    vm = test_stub.create_vm(vm_name = 'vm_net_qos', \
            instance_offering_uuid = new_offering.uuid)
    test_obj_dict.add_vm(vm)

    vm.check()
    vm_inv = vm.get_vm()
    test_stub.make_ssh_no_password(vm_inv)
    test_stub.create_test_file(vm_inv, net_bandwidth)
    test_stub.test_scp_vm_outbound_speed(vm_inv, net_bandwidth)
    if test_stub.test_scp_vm_inbound_speed(vm_inv, net_bandwidth, raise_exception=False):
        test_util.test_fail('VM network inbound is not expected to be limited when only outbound qos is set')

    vm_ops.delete_instance_offering(new_offering_uuid)
    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('VM Network Outbound QoS Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_offering_uuid:
        vm_ops.delete_instance_offering(new_offering_uuid)
