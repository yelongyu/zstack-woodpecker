'''
This case can not execute parallelly
@author: quarkonics
'''
import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global new_offering_uuid
    test_util.test_dsc('Test change VM network bandwidth QoS by 1MB')

    vm = test_stub.create_vm(vm_name = 'vm_net_qos')
    vm.check()
    l3_uuid = vm.get_vm().vmNics[0].l3NetworkUuid
    test_obj_dict.add_vm(vm)

    net_bandwidth = 512
    vm_nic = test_lib.lib_get_vm_nic_by_l3(vm.vm, l3_uuid)
    vm_ops.set_vm_nic_qos(vm_nic.uuid, outboundBandwidth=net_bandwidth*8*1024)
    vm.check()
    time.sleep(1)
    test_stub.make_ssh_no_password(vm.get_vm())
    test_stub.create_test_file(vm.get_vm(), net_bandwidth)
    test_stub.test_scp_vm_outbound_speed(vm.get_vm(), net_bandwidth)

    vm_ops.set_vm_nic_qos(vm_nic.uuid, outboundBandwidth=net_bandwidth*8*1024/2)
    vm.check()
    time.sleep(1)
    test_stub.make_ssh_no_password(vm.get_vm())
    test_stub.create_test_file(vm.get_vm(), net_bandwidth/2)
    test_stub.test_scp_vm_outbound_speed(vm.get_vm(), net_bandwidth/2)

    vm_ops.del_vm_nic_qos(vm_nic.uuid, 'out')
    time.sleep(1)
    if test_stub.test_scp_vm_outbound_speed(vm.get_vm(), net_bandwidth/2, raise_exception=False):
        test_util.test_fail('VM network Outbound is not expected to be limited after qos setting is deleted')

    vm.stop()
    vm.start()
    vm.check()
    if test_stub.test_scp_vm_outbound_speed(vm.get_vm(), net_bandwidth/2, raise_exception=False):
        test_util.test_fail('VM network Outbound is not expected to be limited after qos setting is deleted even after reboot')

    vm.reboot()
    vm.check()
    if test_stub.test_scp_vm_outbound_speed(vm.get_vm(), net_bandwidth/2, raise_exception=False):
        test_util.test_fail('VM network Outbound is not expected to be limited after qos setting is deleted even after reboot')

    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('VM Network QoS change instance offering Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
