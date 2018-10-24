'''
This case can not execute parallelly
@author: Legion
'''
import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

_config_ = {
        'timeout' : 600,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
new_offering_uuid = None

def test():
    global new_offering_uuid
    test_util.test_dsc('Test VM disk bandwidth QoS by 20MB')

    #unit is KB
    write_bandwidth = 15*1024*1024
    read_bandwidth = 20*1024*1024
    new_offering = test_lib.lib_create_instance_offering(read_bandwidth=read_bandwidth, write_bandwidth=write_bandwidth)
    new_offering_uuid = new_offering.uuid

    vm = test_stub.create_vm(vm_name = 'vm_volume_qos', \
            instance_offering_uuid = new_offering.uuid)
    test_obj_dict.add_vm(vm)

    vm.check()

    volume_creation_option = test_util.VolumeOption()
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    
    volume_creation_option.set_name('volume-1')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    vm_inv = vm.get_vm()
    test_lib.lib_mkfs_for_volume(volume.get_volume().uuid, vm_inv)
    mount_point = '/tmp/zstack/test'
    test_stub.attach_mount_volume(volume, vm, mount_point)

    test_stub.make_ssh_no_password(vm_inv)
    test_stub.install_fio(vm_inv)
    if vm_ops.get_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid).volumeBandwidthRead != read_bandwidth and \
    vm_ops.get_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid).volumeBandwidthWrite != write_bandwidth:
        test_util.test_fail('Retrieved disk qos not match')
    test_stub.test_fio_bandwidth(vm_inv, read_bandwidth, '/dev/vda')
    time.sleep(10)
    test_stub.test_fio_bandwidth(vm_inv, write_bandwidth, mount_point)
    vm_ops.delete_instance_offering(new_offering_uuid)
    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('VM Disk read & write QoS Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        vm_ops.delete_instance_offering(new_offering_uuid)
    except:
        pass
