'''
This case can not execute parallelly
@author: Legion
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
    test_util.test_dsc('Test VM disk bandwidth QoS by 20MB')

    #unit is KB
    read_bandwidth = 5*1024*1024
    new_offering = test_lib.lib_create_instance_offering(read_bandwidth = read_bandwidth)

    new_offering_uuid = new_offering.uuid

    vm = test_stub.create_vm(vm_name = 'vm_volume_qos', \
            instance_offering_uuid = new_offering.uuid)
    test_obj_dict.add_vm(vm)

    vm.check()
    vm_inv = vm.get_vm()
    test_stub.make_ssh_no_password(vm_inv)
    test_stub.install_fio(vm_inv)
#     test_stub.test_fio_bandwidth(vm_inv, read_bandwidth, mode='read')
    vm_ops.set_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid, read_bandwidth*2, 'read')
    if vm_ops.get_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid).volumeBandwidthRead != read_bandwidth*2:
        test_util.test_fail('Retrieved disk qos not match')

    test_stub.test_fio_bandwidth(vm_inv, read_bandwidth*2, '/dev/vda')
    vm_ops.del_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid, mode='all')
    if test_stub.test_fio_bandwidth(vm_inv, read_bandwidth, '/dev/vda', raise_exception=False):
        test_util.test_fail('disk qos is not expected to have limit after qos setting is deleted')
    vm_ops.delete_instance_offering(new_offering_uuid)
    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('VM Network QoS Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_offering_uuid:
        vm_ops.delete_instance_offering(new_offering_uuid)
