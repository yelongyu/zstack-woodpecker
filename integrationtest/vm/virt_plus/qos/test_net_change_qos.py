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
    test_util.test_dsc('Test VM network bandwidth QoS by 1MB')

    #unit is KB
    net_bandwidth1 = 1024
    new_offering1 = test_lib.lib_create_instance_offering(net_outbound_bandwidth = net_bandwidth1)

    test_obj_dict.add_instance_offering(new_offering1)
    new_offering_uuid = new_offering1.uuid

    vm = test_stub.create_vm(vm_name = 'vm_net_qos', \
            instance_offering_uuid = new_offering1.uuid)
    test_obj_dict.add_vm(vm)

    vm.stop()

    net_bandwidth2 = 512
    new_offering2 = test_lib.lib_create_instance_offering(net_outbound_bandwidth = net_bandwidth2)

    test_obj_dict.add_instance_offering(new_offering2)
    new_offering_uuid = new_offering2.uuid
    vm_inv = vm.get_vm()
    vm.change_instance_offering(new_offering_uuid)
    vm.start()
    vm.check()
    import time
    time.sleep(1)
    test_stub.make_ssh_no_password(vm_inv)
    test_stub.create_test_file(vm_inv, net_bandwidth2)
    test_stub.test_scp_vm_outbound_speed(vm_inv, net_bandwidth2)
    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('VM Network QoS change instance offering Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
